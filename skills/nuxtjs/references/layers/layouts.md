# 模板外壳、布局与主题

适用范围：修改框架布局、外壳选择、主题偏好或切换保护时必须读取，同时读取 [core 边界](core.md)。只有实际消费版本已包含 templates/themes layer 时才允许使用；普通页面任务禁止新建多外壳体系。

## 归属与偏好

- 稳定布局入口必须在 `layers/core/layouts/<name>/index.vue`；仅有一套外壳时私有区块就近拆分。必须仅识别目录的 index.vue，禁止把私有子组件递归登记为独立布局。
- 已明确需要多外壳时，结构必须放 `layers/templates/<template>/<layout>/index.vue`，配色放 `layers/themes`。必须使用实际注册和异步 loader，非法偏好或缺少布局必须回退 default；禁止按模板复制业务页面/API。
- 模板、layout 与主题是独立语义；模板和主题 Cookie 必须分别维护，SSR 与客户端必须读取相同偏好。已有有效 Cookie 必须保留，隐藏选择入口不等于清除偏好。
- 个人中心导航属于布局，页面通过插槽渲染；框架账号组件与公共词条必须放 core 并同步迁移导入和样式，不得因页面位于 src/pages 就将基础账号导航改成业务私有。
- 切换前必须先加载目标，并保护未保存表单、提交与上传；取消/失败保留原页。保护函数随作用域注销，禁止把密码或表单数据持久化到 Cookie/框架 store。

## 正向结构与反例

```text
layers/core/layouts/user/index.vue
layers/templates/default/user/index.vue
layers/templates/default/user/navigation/index.vue
layers/themes/
```

反例：把 navigation/index.vue 当作 Nuxt 独立布局，或通过配色开关强制重置用户已选模板。

## 完成标准

必须验证默认、非法偏好、缺少布局、SSR/hydration 一致性、用户中心导航高亮、切换取消/加载失败与未保存表单保护；必须运行实际 template 测试、typecheck、build 并浏览器检查消费页面。
