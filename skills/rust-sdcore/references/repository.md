---
name: rust-sdcore-repository
description: sdcore Rust 框架的实际依赖来源定位、仓库身份验证与跨仓库安全边界
---

# Rust sdcore 源码与固定版本

适用范围：定位 SDKit Rust 底座、修改 Cargo 依赖、维护共享源码，以及执行消费方版本升级时必须读取。此 Skill 专用于 SDKit Rust 底座。

## 权威来源与身份

- 已确认的权威公开仓库为 `https://github.com/huwenlong92/sdkit-rust`；Cargo Git URL 为 `https://github.com/huwenlong92/sdkit-rust.git`，crate 名为 `sdcore`，源码位于仓库的 `crates/sdcore`。禁止将仓库名当作 crate 名，或猜测另一个同名仓库。
- 必须从目标项目的 Cargo.toml、Cargo.lock、workspace、features 与 Cargo 实际解析结果确认当前依赖。已知权威仓库不代表目标项目已迁移；旧 path、其他 Git 来源或本地 patch 必须如实识别，禁止未经授权自动切换。
- 公开 HTTPS 底座依赖不需要 GitHub 账号、SSH key 或 CI secret；禁止为该依赖额外配置凭据。消费方其他私有依赖仍按各自已核验来源和权限处理，禁止批量删除认证配置。
- 只读取已授权访问的源码。本地 checkout 路径必须动态发现并核对 Git remote；禁止写死工作站路径，禁止直接编辑 Cargo 缓存中的依赖源码。

## 消费方固定依赖

- 正式依赖必须使用已发布的固定 tag，并提交 Cargo.lock；禁止依赖 main、其他浮动 branch 或自动追随最新版本。版本号必须来自当前项目或本次已确认的升级目标，禁止把文档示例当成永久指定版本。
- 必须核对 Cargo.lock 中 Git source 的完整 commit、声明的 tag、实际解析到的 sdcore 路径与 features 一致。读取 API 必须使用该 commit 的源码；禁止将 main 或本机另一个 revision 的 API 当作已消费能力。
- 应用构建、CI、容器及验收中的 Cargo build/check/test 必须保留锁文件并使用 `--locked`。只有执行已授权的依赖解析或升级时才允许更新锁文件；锁文件需要变化时必须审查具体 package/source 差异，禁止通过删除锁文件绕过失败。
- 必须按已锁定版本的 Cargo.toml 核对 features，保留业务所需能力；禁止为迁移底座顺带打开全部 features、升级工具链或调整无关依赖。

以下为脱敏写法；实际 URL 和版本必须替换为已核验值，features 必须与项目需要及目标版本匹配：

```toml
[dependencies]
sdcore = { git = "https://github.com/example-org/example-rust-core.git", tag = "vX.Y.Z", default-features = false, features = ["sqlite", "auth", "static-embed"] }
```

```sh
# 在消费项目执行；从输出核对 sdcore 的 source、manifest_path 和实际 features。
cargo metadata --locked --format-version 1
cargo check --locked
```

反例：使用 `branch = "main"`，或声明固定 tag 却按 main 的新 API 编写业务代码。

## 底座修改与升级

- 共享能力必须在已核验的权威源码 checkout 中修改，业务语义仍留在消费项目；修改后按[测试与验收](testing.md)验证共享底座与真实消费方。
- 已发布 tag 禁止移动、删除或覆盖。底座修复或新增能力必须通过新版本 tag 分发；源码提交、tag 发布与消费方升级各自核对授权，禁止从修复源码推导发布或部署权限。
- 消费方升级必须显式修改 tag，解析并审查 Cargo.lock 的 commit、features 和依赖变化，然后使用 `--locked` 完成编译、相关测试及本次影响的运行链路；禁止把底座 main 更新或发布成功当成消费方已升级。
- 本地 path/patch 联调必须限定在开发工作区并核对生效来源；交付前必须恢复正式固定 Git 依赖、清除临时覆盖，并重新验证实际解析结果。禁止将本机 SDK 挂载或临时 path/patch 当作发布前提。
- 本地、CI 与 Docker 必须使用同一固定 tag 和锁文件。迁移旧本地 SDK 构建上下文时，必须保留已有前端等其他上下文和发布副作用；禁止为依赖迁移顺带上传制品、更新服务或改造文件布局。

## 入口兼容

- 本旧入口仅用于明确指定 `rust-sdcore` 的历史安装、兼容检查或迁移任务；正常开发必须使用 `sdkit-rust-core`，禁止将本旧入口与新入口重复用于同一任务。

## 完成标准

- 能列出目标项目实际使用的仓库、crate、tag、完整 commit、features 与解析路径，源码和依赖声明一致。
- 已发布 tag 保持不变；升级差异、锁文件和定向验收结果可核验，未执行的发布或运行验证必须明确。
- 人工核对 CI、容器及正式依赖没有遗留本机 SDK 前提或临时 patch；未授权的认证、业务、工具链与线上状态保持不变。
