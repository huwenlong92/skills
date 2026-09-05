---
name: vab-admin-remote-options
description: Vab Admin 远端注册表 options 的语义组件、Pinia 缓存、pending 去重和刷新协议
---

# 远端 options 组件规范

本文适用于后台可维护注册表的 options API、展示组件、select/radio/checkbox 组件和 `src/store/modules` 缓存。数据是否属于远端注册表必须先按 [business-options.md](business-options.md) 判定；组件放置必须同时读取 [placement.md](placement.md)。

## 完整调用链

```text
versioned API
  -> src/api/<domain>/<resource>.ts
  -> src/store/modules/<domain>.ts
  -> <resource>/index.vue、select.vue、radio.vue 或 checkbox.vue
  -> 页面只消费语义组件
```

- 远端 options 必须通过项目已有版本化 API 和统一 request wrapper 获取，禁止新增无版本旁路接口。
- store 是远端 options、loaded、loading、pending 和 label lookup 的唯一状态所有者。
- 语义组件必须自己调用 store 的 fetch/ensure action；页面禁止为了组件回显而重复请求同一 options。
- 页面只有在多个 options 必须与页面主数据同时完成后再整体渲染时，才允许主动调用同一个 store action；组件再次调用必须命中 cache 或 pending，不能产生第二次请求。
- 页面禁止直接复制 API 结果、维护第二份 ref 或硬编码 fallback 数组。

## 目录与命名

- 组件目录使用资源的短单数语义，例如 `target-type`、`region`、`category`；位置由 [placement.md](placement.md) 的真实调用范围决定。
- 展示入口为 `index.vue`，选择输入为 `select.vue`；只有存在真实调用方时才增加 `radio.vue` 或 `checkbox.vue`。
- store 必须按业务域命名，例如 `src/store/modules/catalog.ts`；禁止为每个 select 创建 `item-type-options.ts` 一类 store。
- store state 使用资源复数名，例如 `itemTypes`；action 使用 `fetchItemTypes`、`refreshItemTypes`，label resolver 使用 `itemTypeLabel`。禁止堆叠 `OptionsCacheData` 等实现后缀。

## 单组 options store 协议

有效空数组必须被视为已加载，因此必须使用独立 `loaded` 状态，禁止只用 `list.length` 判断缓存：

```ts
import { getItemTypeOptions, type ItemTypeOption } from '/@/api/catalog/item-type.ts'

type CatalogState = {
  itemTypes: ItemTypeOption[]
  itemTypesLoaded: boolean
  loading: {
    itemTypes: boolean
  }
}

// Promise 不进入 state；按 store 实例隔离，避免 SSR 或多个 Pinia 实例串请求。
const itemTypesPending = new WeakMap<object, Promise<ItemTypeOption[]>>()

export const useCatalogStore = defineStore('catalog', {
  state: (): CatalogState => ({
    itemTypes: [],
    itemTypesLoaded: false,
    loading: {
      itemTypes: false,
    },
  }),
  actions: {
    async fetchItemTypes(): Promise<ItemTypeOption[]> {
      const pending = itemTypesPending.get(this)
      if (pending) return pending
      if (this.itemTypesLoaded) return this.itemTypes

      this.loading.itemTypes = true
      const request = getItemTypeOptions()
        .then((list) => {
          this.itemTypes = list
          this.itemTypesLoaded = true
          return this.itemTypes
        })
        .finally(() => {
          itemTypesPending.delete(this)
          this.loading.itemTypes = false
        })

      itemTypesPending.set(this, request)
      return request
    },
    async refreshItemTypes(): Promise<ItemTypeOption[]> {
      // 已在途的请求可能早于维护操作，不能拿它作为刷新结果。
      const pending = itemTypesPending.get(this)
      if (pending) {
        try { await pending } catch { /* 旧请求失败也必须重新获取。 */ }
      }
      this.itemTypesLoaded = false
      return this.fetchItemTypes()
    },
    itemTypeLabel(value?: string) {
      if (!value) return '--'
      return this.itemTypes.find((item) => item.value === value)?.label || value
    },
  },
})
```

- pending promise 必须由对应 store 实例持有，允许使用模块内以 store 实例为 key 的 WeakMap；禁止放入 Pinia state 或使用跨实例共享的单个 promise。
- 普通 fetch 必须复用 pending，再检查 cache；refresh 必须等待旧 pending 结束后使 loaded 失效并重新 fetch，禁止直接返回维护前的 pending。相同 key 的请求必须去重。
- 请求成功后必须同时写入 list 和 loaded；请求失败时不得把未取得的数据标记为 loaded。
- `.finally()` 必须同时清理 pending 和 loading；错误必须继续向调用方抛出。
- 受登录身份或租户范围影响的 options 禁止使用这套无参数单组缓存，必须按下一节把 identity、workspace 或 tenant 标识纳入参数 key。

API 函数 `getItemTypeOptions()` 的返回类型必须为 `Promise<ItemTypeOption[]>`，与后端直接返回 options 数组的协议一致。现有接口确实返回对象时，只允许在 API 模块按其明确类型解包一次；禁止用 `data.list || []` 掩盖协议不匹配。

上例只适用于不随身份和租户变化的单组 options。清缓存、退出登录或切换上下文时，必须通过请求代次或上下文快照阻止旧响应回写；仅清空数组或删除 pending 不够。参数化缓存的 pending 也必须按 store 实例隔离，禁止共享模块级请求字典。

## 参数化 options

options 由其他字段决定时，store 必须按参数 key 分别缓存：

```ts
const itemKey = (category?: string, status = 1) => JSON.stringify([category ?? '', status])

type CatalogState = {
  items: Record<string, ItemOption[]>
  itemsLoaded: Record<string, boolean>
  loading: {
    items: Record<string, boolean>
  }
}

// 每个 store 实例分别持有这份按参数 key 索引的 pending。
type ItemPending = Map<string, Promise<ItemOption[]>>
```

- key builder 必须定义在 store 文件并由 fetch、options accessor、loading accessor 和 label resolver 共用，禁止各组件自行拼 key；数据受 identity、workspace 或 tenant 影响时必须把对应稳定标识加入 key。
- 必填依赖为空时 fetch 必须直接返回空数组，且不能发请求。
- store 必须提供 `itemOptions(...)`、`isItemLoading(...)` 和 `itemLabel(...)` 一类只读 resolver。
- `refreshItems(...)` 必须只刷新受影响 key；只有后台变更会影响所有参数组合时才允许清空整组缓存。
- 依赖 props 在 mounted 后仍会更新的组件必须使用 `watch(dependencies, fetch, { immediate: true })`，禁止只在 `onMounted` 请求初始参数。

## 展示组件

展示组件必须自行确保 store 已加载，并从 store resolver 取得 label：

```vue
<template>
  <el-link v-if="mode === 'link'" underline="never">{{ label }}</el-link>
  <el-tag v-else-if="mode === 'tag'" effect="plain">{{ label }}</el-tag>
  <span v-else>{{ label }}</span>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import type { ModeType } from '/@/composables/useStatusRender.ts'
import { useCatalogStore } from '/@/store/modules/catalog.ts'

defineOptions({ name: 'ItemType' })

const props = withDefaults(defineProps<{ value?: string; mode?: ModeType }>(), { mode: 'text' })
const catalogStore = useCatalogStore()
const label = computed(() => catalogStore.itemTypeLabel(props.value))

onMounted(() => catalogStore.fetchItemTypes())
</script>
```

- API 只返回 value/label 时，tag 必须使用中性 `plain` 展示，禁止前端凭 value 猜颜色。
- API 明确返回符合 `StatusOption` 的视觉元数据时，展示组件允许复用 [enum-components.md](enum-components.md) 的 `useStatusRender` 模板；禁止另建第二个渲染 composable。
- 未加载时允许显示原始 value 或 `--`，加载完成后必须自动更新 label。

## 输入组件

```vue
<template>
  <el-select v-model="selected" :loading="catalogStore.loading.itemTypes" v-bind="$attrs">
    <el-option v-for="item in catalogStore.itemTypes" :key="item.value" :label="item.label" :value="item.value" />
  </el-select>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCatalogStore } from '/@/store/modules/catalog.ts'

defineOptions({ name: 'ItemTypeSelect' })

const props = defineProps<{ value?: string }>()
const emit = defineEmits<{ (event: 'update:value', value?: string): void }>()
const catalogStore = useCatalogStore()
const selected = computed({
  get: () => props.value,
  set: (value?: string | '') => emit('update:value', value === '' ? undefined : value),
})

onMounted(() => catalogStore.fetchItemTypes())
</script>
```

- 输入组件必须把 store loading 传给 Element Plus，并把 `$attrs` 传给根输入组件。
- 编辑表单已有 value 时，组件挂载后必须立即请求或命中缓存，禁止等下拉展开。
- 只有同一组件存在真实单选与多选调用时才允许增加 `multiple` prop；此时 value 类型必须显式区分单值与数组。否则必须保持单值组件。
- 组件禁止直接 import API、持有第二份 options ref 或在父页面要求传入 options。

## 刷新与组合加载

- 注册表 create、update、delete、enable、disable 或 reorder 成功后，维护组件必须调用对应 `refreshXxx()`。
- 普通列表 `reload` 不能替代 options refresh；父页面协调两者时必须显式执行两项操作。
- 多组 options 只有在相同页面流程中总是一起使用时，才允许 store 提供 `ensureOptions()`、`refreshOptions()`、`currentOptions()` 和统一 pending；任何一组存在独立调用方时必须保留独立 fetch action。

## 验收

- 必须从版本化 API 一直检查到语义组件，确认页面没有硬编码数组、重复请求或第二份 options state。
- 必须验证有效空列表只请求一次、同屏多个组件共享 pending、失败后 loading/pending 清理且下次可以重试。
- 必须模拟“旧请求在途时维护成功”，确认 refresh 发起维护成功后的新请求；必须模拟切换上下文后旧请求才返回，确认不会回写当前缓存。
- 必须验证编辑回显、显式 refresh、注册表维护后刷新，以及 identity、workspace 或 tenant 切换后的 key 隔离。
- 参数化 options 必须验证不同 key 隔离、依赖变化重新加载、缺少依赖不发请求。
- 必须对 store、API 和组件运行项目 ESLint 与 typecheck。
