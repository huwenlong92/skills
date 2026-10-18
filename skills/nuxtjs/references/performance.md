# 生产性能与 SSR 验收

适用范围：修改 Nuxt 门户首屏、SSR/hydration、资源体积、预取、分包或压缩缓存时必须读取。实现必须以当前项目锁定版本为准；允许修改已定位的问题配置与资源，禁止借优化升级模板、关闭鉴权、删除旧引用资源或擅自发布。

## 先测量再修改

- 必须在相同设备、网络、页面、缓存及节流条件下，对生产构建多次采样冷访问、缓存访问和站内导航；性能采样禁止并发争抢带宽。
- 必须分别记录 TTFB、LCP、交互、请求数、实际传输字节与错误。Network 的 Queueing、Connect、TTFB、Download 必须分开判断；JS 执行必须查主线程记录，禁止把请求耗时当执行耗时。SSE 长连接不算静态资源加载失败。
- SSR 首屏必须通过现有请求封装与 `useAsyncData`/`useFetch` 复用 payload；必须核对原始 HTML、payload、用户态与 hydration 一致，无客户端重复请求且失败可重试。禁止整页 ClientOnly、关闭 SSR 或吞警告作为通用修复。
- SSR 内网 API 地址必须按实际 server adapter/private config 解析；本模板不同版本的字段名必须实查，禁止假造 `apiInternalBase` 或泄露内网地址到 public config。容器中的 localhost 不能代替其他服务名。

## 资源、预取与压缩

- 图片必须按展示尺寸和画质评估 WebP/AVIF；只有确认引用迁移后才允许清理原资源，LCP 图片禁止统一 lazy。
- 必须实测代理入口 Content-Encoding、Vary、压缩传输字节；生成压缩文件不等于已被使用。哈希资源允许长期缓存，HTML、用户态 API/payload 禁止套 immutable。滚动发布必须保留仍被旧页面使用的哈希资源。
- SSE 必须保持流式、关闭代理缓冲及造成延迟的压缩；代理变更必须先做配置检查，再按授权 reload 并检查实际入口。
- 只有瀑布图证明预取竞争时才允许调整预取；局部问题必须先局部设置 NuxtLink，只有全站链接行为有同类证据时才允许改全局默认。manifest 预取与链接预取必须分别检查，禁止误删当前页 preload/modulepreload。
- Vite warmup/optimizeDeps 不能作为生产优化证据；禁止机械合并所有 node_modules 或提前加载大型异步依赖。分包必须同时比较字节、请求、缓存与副作用。

## 典型形态与反例

仅当确认当前 Nuxt 支持并且全局预取竞争成立时，允许如下配置：

```ts
experimental: { defaults: { nuxtLink: { prefetchOn: { visibility: false, interaction: true } } } }
```

反例：没有测量就同时关闭所有预取与 preload，并用单次 curl 耗时声称页面提速。触屏没有悬停，必须测试点击、键盘焦点、返回导航。

## 完成标准

必须运行类型检查及生产 build，并用浏览器检查桌面/移动端首屏、错误恢复、导航、hydration。必须在同口径下比较前后指标，记录新增与既有错误；禁止用字节下降比例冒充用户耗时收益。发布必须另有授权、回退版本及真实入口复测；本规范不授权发布。
