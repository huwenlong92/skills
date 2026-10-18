# Realtime 接入与生命周期

适用范围：修改此 Nuxt 模板的 SSE/WebSocket 配置、业务订阅、连接与重连时必须读取。仅当实际消费版本包含 `layers/core/realtime` 与 `useRealtime` 时允许采用下述 API；否则必须先报告能力缺口，禁止虚构能力或擅自升级模板。

## 放置与开关

- 通用传输和连接管理必须放 `layers/core/realtime`，项目应用级事件处理必须放 `src/plugins/realtime-events.client.ts` 或所属业务 module；禁止在页面复制传输实现。
- 开关必须映射 `runtimeConfig.public.realtime.enabled`，`NUXT_PUBLIC_REALTIME_ENABLED` 只有字符串 `true` 才启用。关闭时禁止建立连接或创建重连定时器。
- 基础地址使用 `NUXT_PUBLIC_REALTIME_URL`；完整覆盖使用 `NUXT_PUBLIC_REALTIME_SSE_URL`、`NUXT_PUBLIC_REALTIME_WS_URL`。基础路径前缀必须保留，留空时使用站点同源 `/realtime/sse`、`/realtime/ws`，不得混同 Web API base。
- 必须按实际 runtimeConfig 层级注入运行期配置；普通 Node 启动不自动读取 `.env.production`。HTTPS 页面必须使用 HTTPS/WSS；SSE 网关必须关闭缓冲并核验流式到达，跨域连接必须核验 Cookie/CORS。禁止把 session 标记当 token 放进 URL。

## 订阅契约

- 默认 SSE、`authenticated: true`，必须等待登录；只有公开广播允许显式 false，此参数不赋予后端权限。
- 每次调用建立独立 channel；同一业务订阅跨组件共享时必须放在共同父级或项目管理入口，禁止重复建立连接。
- 订阅参数在创建时固定；切换业务对象必须先 dispose 旧 channel 再创建新的。组件作用域结束必须释放，手动 close 可暂停、connect 可恢复；dispose 后不得重用。
- SSE send 必须返回 false；只有已打开的 WebSocket 允许发送 action。必须在重连 onOpen 后按业务协议恢复订阅/重新读取数据，禁止承诺离线消息自动补发。
- SSE JSON 必须解析为对象，文本保留原值；WS 按 event/action 匹配并保留完整包。用户身份必须由后端认证，不接受客户端用户 ID 替代。

## 正向形态

```ts
const channel = useRealtime({
  events: ['catalog.item.changed'],
  query: { room: `catalog:${itemID}` },
  onEvent: async () => { await refreshItem() },
})
```

这是虚构业务事件，接入前必须核对后端事件注册、room 与权限。反例：路由参数变了仍复用旧订阅，或将连接对象放入 Pinia/SSR payload。

## 完成标准

必须验证 SSR 不连接、不启动定时器；每个 Nuxt app 独立实例；登录/退出/用户变化关闭旧连接；pagehide/离线暂停、pageshow/在线恢复；主动关闭、卸载、HMR 清理定时器及旧回调。必须核验现有退避上限和连接成功后重置，不把浏览器网络中断冒充业务回调异常。必须运行实际 realtime 测试、typecheck、build；多端 Cookie 并存时人工检查目标端身份、网关鉴权和流式响应。
