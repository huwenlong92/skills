---
name: nuxtjs-remote-options
description: Nuxt.js 远端注册表 options 的语义组件、Pinia 缓存、pending 去重、SSR hydrate 和刷新协议
---

# 远端 options 组件规范

本文适用于后台可维护注册表的 options API、展示组件、select/radio/checkbox 组件、`src/store/modules` 缓存和 SSR hydrate。数据是否属于远端注册表必须先按 [business-options.md](business-options.md) 判定；组件放置必须同时读取 [placement.md](placement.md)。

## 完整调用链

```text
versioned API
  -> src/api/<domain>/<resource>.ts
  -> src/store/modules/<domain>.ts
  -> <resource>/index.vue、select.vue、radio.vue 或 checkbox.vue
  -> 页面只消费语义组件
```

- 远端 options 必须通过项目已有版本化 API 和 `useAppRequest()` 获取，禁止新增无版本旁路接口或直接 `$fetch`。
- store 是远端 options、loaded、loading、pending、hydrate 和 label lookup 的唯一状态所有者。
- 语义组件必须自己调用 store 的 fetch/ensure action；页面禁止为了组件回显而重复请求同一 options。
- 页面只有在多个 options 必须与页面主数据同时完成后再整体渲染或 SSR 首屏必须包含 options 时，才允许主动调用同一个 store action；组件再次调用必须命中 cache 或 pending。
- 页面禁止直接复制 API 结果、维护第二份 ref 或硬编码 fallback 数组。

## 目录与命名

- 组件目录使用资源的短单数语义；位置由 [placement.md](placement.md) 的真实调用范围决定。
- 展示入口为 `index.vue`，选择输入为 `select.vue`；只有存在真实调用方时才增加 `radio.vue` 或 `checkbox.vue`。
- store 必须按业务域命名，例如 `src/store/modules/catalog.ts`；禁止为每个 select 创建单独的 options store。
- store state 使用资源复数名，action 使用 `fetchItemTypes`、`refreshItemTypes`，label resolver 使用 `itemTypeLabel`。

## Store 基础协议

- 每组 options 必须拥有 list、loaded 和 loading；有效空数组必须标记为 loaded，禁止只用 `list.length` 判断缓存。
- pending promise 必须由对应 store 实例持有，允许使用模块内以 store 实例为 key 的 WeakMap；禁止放入可序列化 Pinia state 或使用跨实例共享的单个 promise。
- 普通 fetch 必须先复用 pending，再检查 loaded cache；否则设置 loading 并发起请求。
- 请求成功后必须写入 list 和 loaded；请求失败时不得写 loaded；`.finally()` 必须清理 pending 和 loading，并让错误继续抛出。
- store 必须提供无参数或同参数的 `refreshXxx()`，等待旧 pending 结束后使 loaded 失效并重新 fetch；禁止直接返回维护前的 pending。
- 受登录身份、workspace 或租户影响的 options 禁止使用无参数单组缓存，必须把对应稳定标识纳入参数 key。

实现形态必须保持以下结构：

```ts
// Promise 不进入 state；按 store 实例隔离，避免 SSR 或多个 Pinia 实例串请求。
const itemTypesPending = new WeakMap<object, Promise<ItemTypeOption[]>>()

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    itemTypes: [] as ItemTypeOption[],
    itemTypesLoaded: false,
    loading: { itemTypes: false },
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

API 函数 `getItemTypeOptions()` 的返回类型必须为 `Promise<ItemTypeOption[]>`，与后端直接返回 options 数组的协议一致。现有接口确实返回对象时，只允许在 API 模块按其明确类型解包一次；禁止用 `data.list || []` 掩盖协议不匹配。

上例只适用于不随身份和租户变化的单组 options。清缓存、退出登录或切换上下文时，必须通过请求代次或上下文快照阻止旧响应回写；仅清空数组或删除 pending 不够。参数化缓存的 pending 也必须按 store 实例隔离，禁止共享模块级请求字典。

## 参数化 options

- options 由其他字段决定时，store 必须以一个稳定 key builder 为 list、loaded、loading、pending 和 label resolver 建立相同 key。
- key builder 必须位于 store 文件，禁止组件和页面自行拼 key；数据受 identity、workspace 或 tenant 影响时必须把对应稳定标识加入 key。
- 必填依赖为空时 fetch 必须直接返回空数组并且不发请求。
- store 必须提供 `xxxOptions(...)`、`isXxxLoading(...)` 和 `xxxLabel(...)` 只读 resolver。
- `refreshXxx(...)` 必须只刷新受影响 key；只有后台变更影响所有参数组合时才允许清空整组缓存。
- 依赖 props 变化的组件必须使用 `watch(dependencies, fetch, { immediate: true })`。

## 语义组件

- 展示组件必须支持 `tag`、`link`、`text` 中实际使用的 mode，自行 fetch，并通过 store label resolver 渲染。
- API 只返回 value/label 时，tag 必须使用中性 `plain` 展示，禁止前端凭 value 猜颜色。
- API 明确返回符合 `StatusOption` 的视觉元数据时，必须复用 [enum-components.md](enum-components.md) 的 `useStatusRender` 协议。
- 输入组件必须直接读取 store options 与 loading，使用 computed 代理暴露 `v-model:value`，并把 `$attrs` 传给 Element Plus 输入组件。
- 编辑表单已有 value 时，组件必须立即 fetch 或命中 cache，禁止等下拉展开。
- 组件禁止直接 import API、持有第二份 options ref 或要求父页面传入 options。
- 只有同一组件存在真实单选与多选调用时才允许增加 `multiple` prop 并显式区分单值与数组；否则保持单值组件。

## SSR hydrate

- 普通交互表单 options 由客户端语义组件加载，不得自动提升为 SSR bootstrap。
- 只有首屏 HTML 必须显示对应 label/options 且数据跨页面复用时，才允许服务端请求并调用 store 的 `hydrateXxx()`。
- `hydrateXxx()` 必须同时写入 list 和 loaded；客户端组件随后调用 fetch 必须命中缓存。
- private upstream 和凭据必须留在 server adapter；Pinia state 只能接收允许发送给当前请求用户的数据，禁止包含服务端秘密。
- pending promise 不参与 SSR 序列化，且必须按当前请求的 Pinia store 实例隔离；禁止跨 SSR 请求复用模块单例状态，原因见 [Vue SSR 状态隔离](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution)。

## 刷新与组合加载

- 注册表 create、update、delete、enable、disable 或 reorder 成功后，维护组件必须调用对应 `refreshXxx()`。
- 普通页面 reload 不能替代 options refresh；需要两者时必须显式执行两项操作。
- 多组 options 只有在同一页面流程中总是一起使用时，才允许提供 `ensureOptions()`、`refreshOptions()`、`currentOptions()`、`hydrateOptions()` 和统一 pending；任何一组存在独立调用方时必须保留独立 fetch action。

## 验收

- 必须从版本化 API 一直检查到语义组件，确认页面没有硬编码数组、直接 `$fetch`、重复请求或第二份 options state。
- 必须验证有效空列表只请求一次、同屏多个组件共享 pending、失败后 loading/pending 清理且下次可以重试。
- 必须模拟“旧请求在途时维护成功”，确认 refresh 发起维护成功后的新请求；必须模拟切换上下文后旧请求才返回，确认不会回写当前缓存。
- 必须验证编辑回显、显式 refresh、注册表维护后刷新、上下文 key 隔离和 SSR hydrate 后客户端不重复请求；两个并行 SSR 请求必须使用不同的 store 与 pending。
- 参数化 options 必须验证不同 key 隔离、依赖变化重新加载、缺少依赖不发请求。
- 必须对 store、API 和组件运行项目 format、ESLint 与 typecheck。
