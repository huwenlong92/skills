# 上线验收

适用范围：部署后检查、域名排查、Binding 排查和交付报告时必须读取。

## 探针与人工检查

- 必须先确认接口只读且不会直接或间接触达正式数据库；未知接口停止探测。禁止为验收创建内容、覆盖 R2 Latest、发消息或调用任务触发接口。
- 必须分别验收本次部署版本地址与用户要求的正式入口；版本 URL 通过不能代表正式域名切换完成。生产入口必须核对 TLS、自定义域名状态、缓存和实际版本，不能只验证 Pages 默认域名。
- 探针必须检查状态码、Content-Type、预期正文特征；静态资源必须验证真实 JS/CSS 响应，禁止把 SPA HTML fallback 当作资源成功。
- 重定向默认失败；需要跳转时单独检查 Location，再对明确授权的目标执行检查，禁止自动跨域跟随并把登录页视为业务成功。
- SSR 必须检查直接 GET HTML 的真实正文；不能以客户端挂载后文字证明服务端渲染。Binding 必须通过已授权只读链路验证，不能只看本地配置。
- 当前助手仅支持公开或 localhost 的 GET 探针，不处理凭据、Cookie 或 Access bypass；私有入口必须沿用项目已授权的认证验收，禁止为探针临时移除保护。
- 桌面/移动导航、登录状态、交互、错误页、分享与权限隔离必须按项目验收范围人工或浏览器检查，HTTP 探针不能代替它们。

## 正向形态

计划中的 probes 使用路径、精确状态、类型和不含私密数据的内容标识：

```json
{"path":"/docs/getting-started","status":200,"content_type":"text/html","contains":"Getting started"}
```

```sh
python3 .sdkit/cloudflare/cfops.py verify --target review \
  --origin https://review.example.invalid
```

示例域名仅表达参数形态；实际 origin 必须来自刚读回的部署结果。反例：只执行 `curl -I /`，看到 200 就宣布 SSR、资源和域名全部验收成功。

## 完成标准

每个探针独立报告 PASS/FAIL；任一超时、跳转、状态/类型/正文不符均非零退出。必须核对本次部署版本与正式入口对应关系，人工检查项目关键路径和浏览器行为；未验证项逐项保留。
