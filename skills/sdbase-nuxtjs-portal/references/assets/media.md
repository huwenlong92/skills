---
name: nuxtjs-assets-media
description: Nuxt.js public、业务 assets、自定义 SVG、core assets 和远端图片的放置规则
---

# 图片与资源规范

本文适用于新增、移动或修改 `public`、`src/assets`、`src/icon`、`layers/core/assets` 以及后端或 CDN 图片引用。

## 目录边界

- 需要稳定 URL 原样访问的 favicon、logo 或公开文件必须放在 `public`，引用路径以 `/` 开头并验证 base URL。
- 只由前端代码使用且需要 Vite/Nuxt 处理的业务图片和局部样式资源必须放在 `src/assets`。
- 业务自定义 SVG 必须放在 `src/icon`；插画类 SVG 放在 `src/icon/illustration`。
- 字体、框架全局样式、theme、token 和 Element Plus 覆盖必须放在 `layers/core/assets`。
- 业务图片、产品品牌插画和营销图禁止进入 core assets；框架 token 禁止进入业务 assets。

## 命名与复用

- 图标和资源目录必须使用小写 kebab-case；历史文件不在任务范围内时禁止为统一命名批量修改。
- Remix Icon 能准确表达语义时必须使用现有 `VabIcon`；只有没有对应图标时才允许新增 SVG。
- 新增资源前必须搜索相同语义或相同内容，禁止重复提交。
- 后端或 CDN 图片必须通过项目已有 `useCloudImage()` 归一化；只有该 composable 无法处理已确认的新来源时才允许扩展。

## 图片质量

- 门户首屏和内容图片必须表达真实产品、内容或场景，禁止用纯装饰占位图替代核心信息。
- 新增大图必须在提交前压缩到满足项目性能预算；项目没有数值预算时，必须比较同类现有资源并记录文件大小。
- 响应式图片必须检查桌面和移动端的比例、裁切、加载失败和文字覆盖。
- 页面核心操作与信息禁止只存在于图片中。

## 验收

- 每个新增资源必须能说明为何属于 `public`、业务 assets、icon 或 core assets。
- 必须检查没有语义重复图标、未压缩原图或业务资源进入 core。
- 必须在配置的 base URL 下验证 public 路径，并检查后端/CDN 图片归一化结果。
- 页面资源必须人工检查桌面、移动端、加载失败和替代文本。
