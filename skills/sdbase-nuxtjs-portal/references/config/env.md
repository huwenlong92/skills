---
name: nuxtjs-config-env
description: Nuxt.js env、runtime config、API base、部署路径和项目固定配置规则
---

# 配置与环境变量规范

本文适用于修改 `.env*`、`src/config`、根或 core `nuxt.config.ts`、runtime config、API base 与部署路径。

## 配置边界

- `.env` 只放本地开发环境值；生产示例文件只放占位值，禁止写真实密钥。
- `src/config` 只放当前项目固定的 auth、network、display 和 feature 配置，禁止放部署密钥、动态注册表或页面临时字段。
- `layers/core/nuxt.config.ts` 负责 framework modules、alias、CSS、runtime config 和 Vite 基础配置。
- 根 `nuxt.config.ts` 只负责接入 core layer、项目 modules 与项目级覆盖。

## 环境变量

- 浏览器可见变量必须使用 `NUXT_PUBLIC_` 并进入 public runtime config。
- 只在构建、Nitro 或服务端使用的变量必须使用项目私有前缀并进入 private runtime config。
- 密钥、内部地址和服务端 token 禁止使用 `NUXT_PUBLIC_`。
- 业务代码禁止写死 API 域名、部署二级目录或静态资源 base path。
- 新变量语义与现有变量重合时必须复用，禁止建立别名变量。
- 固定项目配置只有需要随部署环境变化时才允许改为环境变量。

## API 与部署路径

- 本地同域代理必须使用 `NUXT_PUBLIC_APP_API_BASE=/api` 和 `NUXT_APP_API_PROXY_TARGET=http://localhost:<port>`；目标项目已有其他变量名时沿用其名称但保持 public/private 边界。
- 生产同域代理必须保持浏览器 API base 为 `/api`，由网关或平台转发。
- 只有部署明确使用独立 API 域名时才允许将完整域名放入 public API base，并必须验证 CORS 与 cookie 策略。
- 二级目录必须由 Nuxt app base 和网关规则处理，业务代码禁止手工拼接。

## 修改门禁

- 修改 `.env*`、runtime config 或 `nuxt.config.ts` 后必须重启开发服务。
- 修改 layout、theme、baseURL、assetsDir、routeRules 或 build 配置后必须运行 production build。
- 增加 public runtime config 前必须确认值允许出现在浏览器源代码和网络请求中；不允许时立即停止并改用 server adapter。

## 验收

- 必须检查 public runtime config 中没有密钥、内部地址或服务端 token。
- 必须检查没有重复语义变量、业务硬编码域名或手工二级路径拼接。
- 环境或 config 修改后必须记录重启和 production build 结果。
- 独立 API 域名必须验证实际浏览器 CORS、cookie 和登录态。
