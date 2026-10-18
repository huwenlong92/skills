---
name: vab-admin-enum-components
description: Vab Admin 固定枚举组件的 options、展示、输入变体和 useStatusRender 协议
---

# 枚举组件规范

本文适用于新增或修改状态、类型、等级、布尔语义等固定代码枚举的展示与输入组件，以及 `src/composables/useStatusRender.ts`。枚举来自后台可维护注册表时必须同时读取 [business-options.md](business-options.md)；组件落点以 [placement.md](placement.md) 为唯一权威。

## 必须组件化的场景

- 页面需要把枚举值转换为文案、tag、link、颜色或图标时，必须创建或复用对应业务枚举组件，禁止在页面内写 `labelMap`、`typeMap`、重复 `el-tag` 分支或三元表达式。
- 筛选、表单和展示使用同一业务枚举时，必须共同读取同一份 options，禁止分别维护数组和文案。
- 只有随代码发布且不能由后台维护的枚举才允许写入本地 `options.ts`。后台可维护数据禁止写死，数据来源按 [business-options.md](business-options.md) 处理。
- 组件从 [placement.md](placement.md) 判定的最窄作用域开始；本文目录结构不构成提升到 `src/components` 的依据。

## 标准目录

```text
<enum>/
├── options.ts
├── index.vue
├── select.vue
├── radio.vue
└── checkbox.vue
```

- `options.ts` 是枚举值、展示文案和视觉元数据的唯一来源。
- 枚举存在展示调用时必须创建 `index.vue`；存在 select、radio 或 checkbox 调用时才创建对应输入文件，禁止创建无调用方的占位变体。
- `index.vue` 只负责展示；`select.vue`、`radio.vue`、`checkbox.vue` 只负责输入。
- 同一枚举的输入变体必须与 `index.vue` 同目录，禁止各页面自行包装一份 options。

## options.ts 契约

`options.ts` 必须导出 `Value`、`Option` 和 `options`；只有存在非组件文本解析调用方时才增加 `label()`。下面示例包含该可选函数：

```ts
import type { StatusOption } from '/@/composables/useStatusRender.ts'

export type Value = 'private' | 'internal' | 'public'
export type Option = StatusOption & { value: Value }

export const options = [
  { value: 'private', label: '仅自己', type: 'info' },
  { value: 'internal', label: '组织内', type: 'warning' },
  { value: 'public', label: '公开', type: 'success' },
] satisfies Option[]

export function label(value?: Value) {
  return options.find((option) => option.value === value)?.label || '--'
}
```

- `Value` 必须对应真实 API 字段类型；API 已导出准确类型时必须直接引用，禁止重新手写第二份 union。
- `Option` 必须扩展 `StatusOption` 并收窄 `value`；业务需要 icon 等额外元数据时在 `Option` 中显式增加。
- `options` 必须使用 `satisfies Option[]`，禁止用宽泛类型注解丢失字面量类型。
- 标准视觉字段只使用 `type`、`effect`、`color`、`textColor`、`hoverColor`、`borderColor` 和 `loading`，禁止新增 `tag`、`tagType`、`className` 等平行字段。
- 存在 `label()` 时必须读取同一 `options`。未知值返回 `--`；只有业务合同明确定义缺省枚举值时才允许返回对应文案。该语义解析入口不受普通单次属性读取 helper 限制，但禁止创建没有调用方的函数。
- 数字枚举必须区分 `0` 与未选择，禁止直接用 `Number(null)`、`Number('')` 或 truthy 判断合并两者；布尔枚举禁止用 `Boolean('false')` 转换字符串。默认值必须来自明确业务契约，不能统一默认成 `0`。
- 表单允许值与完整枚举不同且规则稳定时，必须在 `options.ts` 导出语义明确的派生数组，例如 `formOptions`；禁止在多个页面重复 `filter()`。

## useStatusRender 统一协议

所有枚举展示组件必须复用 `src/composables/useStatusRender.ts`，禁止在各组件重复计算 tag/link 样式。项目缺少该文件时，首次增加枚举展示组件必须按以下契约补齐一次，后续只允许复用或扩展统一契约。

```ts
import type { TagProps, LinkProps } from 'element-plus'

export interface StatusOption {
  value: string | number | boolean | undefined
  label: string
  loading?: boolean
  type?: TagProps['type'] | LinkProps['type']
  effect?: TagProps['effect']
  color?: string
  textColor?: string
  hoverColor?: string
  borderColor?: string
}

export type ModeType = 'link' | 'tag' | 'text'
```

`useStatusRender(options, value, mode)` 必须返回以下 computed 数据：

- 当前匹配项 `option`。
- tag 使用的 `tagType`、`tagStyle`、`tagColor`、`tagEffect`。
- link 使用的 `linkType`、`linkStyle`。
- 公共 `label` 和 `loading`。

统一兜底必须是：未知 value 的 label 为 `--`，未知 tag type 为 `info`，未提供 effect 时为 `light`。`textColor`、`borderColor` 和 `hoverColor` 必须转换为 Element Plus CSS variables，禁止由业务组件重复拼样式。该 composable 禁止包含具体枚举值、API 请求、store mutation 或页面行为。

## index.vue 展示组件

标准展示组件必须支持 `tag`、`link`、`text` 三种 mode，默认使用 `tag`：

```vue
<template>
  <el-link v-if="mode === 'link'" :style="linkStyle" :type="linkType" underline="never">
    {{ label }}
  </el-link>
  <el-tag v-else-if="mode === 'tag'" :color="tagColor" :effect="tagEffect" :style="tagStyle" :type="tagType">
    {{ label }}
  </el-tag>
  <span v-else>{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStatusRender, type ModeType } from '/@/composables/useStatusRender.ts'
import { options, type Value } from './options.ts'

defineOptions({ name: 'Visibility' })

const props = withDefaults(defineProps<{ value?: Value; mode?: ModeType }>(), { mode: 'tag' })
const value = computed(() => props.value)
const mode = computed(() => props.mode)

const { tagType, tagStyle, tagColor, tagEffect, linkType, linkStyle, label } = useStatusRender(options, value, mode)
</script>
```

- `value` 类型必须使用 `options.ts` 导出的 `Value`；只有 API 实际存在字符串与数字兼容输入时才允许加入兼容类型并在一个 computed 中归一化。
- `mode` 类型必须使用 `ModeType`，禁止每个组件重复声明 `tag | link | text`。
- 模板必须直接使用 `useStatusRender` 返回值，禁止另写 `getLabel()`、`getType()` 或同义 computed。
- `defineOptions({ name })` 使用业务枚举的最短 PascalCase 名称。

## 特殊展示 mode

当前枚举已经有 icon 等第四种展示形态的真实调用方时，允许在当前枚举组件内扩展 mode；禁止修改所有枚举共享的 `ModeType`：

```ts
type VisibilityModeType = ModeType | 'icon'

const mode = computed<VisibilityModeType>(() => props.mode)
const renderMode = computed<ModeType>(() => (props.mode === 'icon' ? 'text' : props.mode))
const current = computed(() => options.find((option) => option.value === props.value))

const render = useStatusRender(options, value, renderMode)
```

特殊分支必须放在标准 link/tag/text 分支之前，并继续使用同一 options 的 label 与元数据。只有当前枚举的 `Option` 可以增加 icon 等业务字段。

## 输入组件

输入组件必须直接遍历同一 `options`，使用 `v-model:value` 对外暴露值，并通过 computed 代理：

```vue
<template>
  <el-select v-model="selected" :clearable="clearable" :placeholder="placeholder" v-bind="$attrs">
    <el-option v-for="option in options" :key="String(option.value)" :label="option.label" :value="option.value" />
  </el-select>
</template>

<script setup lang="ts">
import { options, type Value } from './options.ts'

defineOptions({ name: 'VisibilitySelect' })

const props = withDefaults(defineProps<{ value?: Value; placeholder?: string; clearable?: boolean }>(), {
  placeholder: '请选择可见范围',
  clearable: false,
})
const emit = defineEmits<{ (event: 'update:value', value?: Value): void }>()

const selected = computed({
  get: () => props.value,
  set: (value?: Value | '') => emit('update:value', value === '' ? undefined : value),
})
</script>
```

- `select.vue` 必须把 `$attrs` 传给 `el-select`，只显式声明业务需要固定的 props。
- `radio.vue` 和 `checkbox.vue` 必须使用同一 options、computed 代理和 `update:value`；`button` 只控制 Element Plus 的 button/普通形态。
- `checkbox.vue` 的 value 必须是 `Value[]`，空值必须映射为空数组；禁止把数组与单值组件合并。
- 输入组件禁止包含展示 mode、tag 样式、API 请求或页面提交逻辑。

## 验收

- 必须检查页面没有新增枚举 label/type map、内联 options 或重复 tag/link 分支。
- 每个固定枚举组件必须具有单一 `options.ts`，导出 `Value`、`Option`、`options` 并使用 `satisfies` 校验；存在 `label()` 时必须检查实际调用方。必须验证空值、合法零值及未知值不会被错误合并。
- 存在展示调用时必须检查 `index.vue` 复用 `useStatusRender` 且支持 tag/link/text；存在输入调用时必须检查对应变体共用同一 options 和 `v-model:value`。
- 必须检查 `useStatusRender` 没有业务枚举、请求或 mutation，未知值、type 和 effect 的兜底符合统一协议。
- 特殊 mode 必须有真实调用方，且没有污染公共 `ModeType`。
- 必须对新增或修改的 Vue/TypeScript 文件运行项目 ESLint 和 typecheck。
