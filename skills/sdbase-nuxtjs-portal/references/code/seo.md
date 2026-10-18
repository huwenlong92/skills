# 页面 SEO 与收录边界

适用范围：修改标题、描述、canonical、分享图、robots、sitemap、多语言 SEO 时必须读取，同时遵守 [页面所有权](page.md)。仅在消费版本实际提供统一 SEO API 时允许使用其名称；缺失时必须报告，不自动升级模板。

## 规则与位置

- 框架 head、URL 与收录机制必须留在 `layers/core`，站点默认配置必须由 runtime config 提供；页面覆盖、业务数据与公开内容路由策略必须由 `src/pages` 拥有，禁止藏入完整页面主体组件。
- 必须复用实际 `useAppSeo` 等统一入口，以 getter/ref 支持 SSR 内容和语言切换；公开详情必须先取得数据，不存在的内容返回 404，禁止生成虚假的成功页面。
- canonical 必须采用显式公开 HTTP(S) 域名并处理 app baseURL，默认排除 hash/tracking query；独立分页仅允许显式保留必要参数。分享图必须为完整 HTTP(S) URL，禁止凭据、协议相对与非 HTTP(S) 地址。
- 测试、预览和开发默认禁止收录；账号、登录、私有及错误页必须 noindex。`publicAccess` 不代表可收录，页面只能进一步禁用，禁止绕过全站禁收录策略。
- robots、sitemap 与页面策略必须一致，只登记真实有效公开内容；禁止伪造 lastmod。框架静态清单不代表业务动态 sitemap 已接入，只有真实本地化 URL 才允许 hreflang。

## 正向形态与反例

```ts
const { data: article } = await useAsyncData('public-article', () => getPublicArticle())
useAppSeo({ title: () => article.value?.title ?? '', noindex: () => !article.value })
```

上例为虚构内容数据；404 分支必须按项目契约另行处理。反例：只更新 document.title，未核对原始 SSR HTML，或将用户账户 URL 填入 sitemap。

## 完成标准

必须在项目 README 链接实际 SEO 接入说明，包含站点配置、SSR getter、canonical、noindex、动态 sitemap 与部署验证。必须检查 SSR HTML 的覆盖、canonical 唯一性、语言、账号/错误页 noindex，并运行实际 SEO 测试、typecheck、build；运行期 robots/sitemap 开关必须单独核验。
