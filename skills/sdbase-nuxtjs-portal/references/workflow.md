---
name: nuxtjs-workflow
description: Nuxt.js 需求从检查运行环境和同类实现到格式化、类型、构建与浏览器验证的执行顺序
---

# Nuxt 工作流程

本文适用于所有 Nuxt.js 创建、修改、重构、评审和调试任务。本文只定义执行顺序；目录、页面、组件、请求和框架边界由对应 reference 唯一定义。

## 动手前

1. 根据 `SKILL.md` 分流表读取全部命中 references；新增或移动文件时必须读取 [structure/directories.md](structure/directories.md)。
2. 检查 Nuxt 版本、`srcDir`、layers、`package.json.packageManager`、Node 版本文件、scripts、路径别名和一个同类页面或组件。
3. 必须使用项目声明的 Node 版本与包管理器，禁止混用 npm、yarn 和 pnpm。
4. 页面任务必须读取 [code/page.md](code/page.md)、[components/placement.md](components/placement.md) 和 [modules/placement.md](modules/placement.md)，先确定页面所有权和区块边界。
5. 只有命中 [layers/core.md](layers/core.md) 的全部能力门禁时才允许修改 `layers/core`。
6. 禁止主动升级 Nuxt、Vue、Element Plus、Pinia 或构建依赖，也禁止格式化任务范围外的文件。

## 实现中

- 新文件必须放入 [structure/directories.md](structure/directories.md) 已定义的目录，禁止为单次需求建立同义分层。
- 页面必须保留 route meta、主数据和区块组合；独立状态区块必须按调用范围拆分。
- 业务代码必须复用现有 request、auth、route、theme 和 token 能力，禁止在页面建立平行底座。
- 抽取共享组件、store 或 composable 后必须删除被替代的重复实现，禁止新旧路径并存。
- 修改 `.env*`、`nuxt.config.ts` 或 layer 配置后必须重启开发服务。

## 格式与验证

1. Vue、TypeScript、JavaScript 和 JSON 必须由项目 Prettier 配置格式化；ESLint 只负责语义与质量检查。
2. 对修改文件执行项目的 format check 和 ESLint 命令；修改 TypeScript、Vue、route、store、composable 或 API 类型后执行 `pnpm typecheck` 或等价项目命令。
3. 修改 layout、theme、route meta、routeRules、runtime config 或部署配置后执行 `pnpm build`。
4. 页面视觉或交互变化必须在浏览器中检查目标桌面宽度和移动端宽度。
5. 无法执行某项检查时，交付说明必须写明未执行项、原因和人工检查对象。

## 编辑器约定

- 项目使用 Prettier 时，根目录必须存在配置，并将 Vue、TypeScript、JavaScript、JSON 的保存格式化交给 Prettier。
- `.vscode/settings.json` 存在时必须设置 `prettier.requireConfig: true`，并禁止 ESLint 同时充当 formatter。
- 项目配置 `singleAttributePerLine`、`bracketSameLine` 或 `htmlWhitespaceSensitivity` 时必须服从项目配置，禁止在 skill 中另造一套格式。

## 验收

- 必须能列出本次命中的 references，并确认每个新增文件通过目录门禁。
- 必须提供实际执行的 format、lint、typecheck、build 或浏览器检查结果；未执行项必须明确说明。
- 必须确认页面所有权清楚、共享能力满足真实调用范围；完整流程转发壳必须满足 [code/page.md](code/page.md) 的多路由例外，禁止为缩短文件新增。
- 必须确认没有升级依赖、混用包管理器、修改无关文件或遗留临时验证文件。
