# 静态设计资产交付契约

适用范围：需要整理高保真 PNG、选择主稿、生成 Manifest、SHA-256 或 ZIP 时读取。

本文件管理离线文件打包；在线 MinIO 版本、授权接收和回读由 [MCP 设计资产交付](mcp-delivery.md) 及服务端实际 `artifact_*` 契约负责。离线 ZIP 不是 MCP 文件集输入，不能把两份 Manifest 直接视为同一 Schema。

- 必须先扫描实际可访问的图片；找不到的历史原图标记 missing，禁止伪造路径或文件。
- 必须从最终目录中实际存在的文件生成 Manifest，path 相对于 Manifest 所在目录，不得带重复顶层目录前缀。
- ZIP 内所有资产路径必须为 ASCII；中文页面名称、模块名称保留为 UTF-8 JSON 字段。
- 模块路径标识必须是安全 ASCII slug，中文模块展示名仅放业务元数据；不得将任意具体产品的模块列表写死为通用 Skill 白名单。
- 禁止保留指向旧 ZIP 的 original_zip_path 等失效字段；源文件名仅作为 source_filename 元数据。
- 每条资产必须记录 path、module、page_id、page_name、kind、sha256、bytes、status；主稿与历史稿必须区分。
- 必须检查重复 SHA-256、路径冲突、路径穿越、损坏 PNG、Manifest 文件存在性和 ZIP 解压完整性。
- 禁止覆盖非空输出目录；原图不得重新编码、缩放或修改字节。
- 只有真实运行校验成功才能宣称完整性通过；超大 ZIP 拆分时必须附可验证的重组步骤和哈希。
- 允许位置：用户指定的交付目录或目标项目明确授权的设计资产目录；禁止擅自写入业务源码、仓库根目录或部署目录。

正向形态：manifest.json 位于交付根目录，path 为 selected/profile/profile-home.png，解压后直接存在该文件。反例：path 为 bundle/selected/中文目录/a.png，但 Manifest 已位于 bundle/。

## 完成标准

Manifest 中每条 path 均可从其所在目录读取，哈希与大小一致；ZIP 中条目及字节逐一匹配；所有非 ASCII 路径、失效字段与路径穿越均被拒绝。
