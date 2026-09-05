---
name: service-excel
description: sdkitgo Excel 导入导出的当前基础边界与同步异步分流规则
---

# Excel 导入导出规范

本文适用于 HTTP Excel import/export、workbook 解析、导出文件生成和导入批量写入。当前只固定已确认的基础边界；具体模板、sheet 名、列名、格式和业务错误文案必须由目标项目的接口契约定义，禁止从本文件虚构。

## 放置位置

- 只有一个导入或导出 endpoint，且不定义 workbook 专属结构时，handler 必须放在所属资源文件中。
- 同一资源存在两个以上 Excel endpoint，或需要定义 workbook 列、行结构、模板校验和解析逻辑时，允许在同一 handler 业务模块下建立 `{resource}_excel.go`。禁止创建跨业务的 `app/http/excel` 或通用 `app/infra/excel` 来收纳单个资源模板。
- 跨项目通用的 workbook reader/writer 机制属于 sdkit `pkg` 候选；当前项目特有的列契约、权限和业务校验必须留在业务 handler 或 worker domain。

## 导出

- Export handler 必须复用与列表接口相同的权限范围和业务筛选语义，但不得调用 HTTP list handler 或先构造其 JSON response。
- 查询、projection 和 workbook 列映射必须在当前导出流程可见；关联数据仍按 [database/projection.md](../database/projection.md) 通过 SQL 形成，禁止逐行补查。
- 文件名、sheet 名和列顺序必须由代码固定；禁止接受客户端提供的文件路径、sheet 表达式或任意 SQL 排序字段。
- 项目已有流式 workbook/下载能力时必须直接写 response stream；只有所用库必须落盘时才允许使用随机临时文件，并必须通过 `defer` 或 `t.Cleanup` 删除。禁止写入固定共享文件名或仓库目录。
- 同步导出必须由接口或配置明确最大行数、HTTP timeout 和内存预算，并在该上限下验证能够完成；缺少任一上限或验收失败时必须改为 worker 生成受权限保护的 artifact，再由 HTTP 接口查询状态或下载。

## 导入

- 读取 workbook 前必须限制上传大小，并校验文件能够被所用 Excel reader 正常打开；扩展名和 MIME 只能作为前置提示，不能替代内容解析。
- 必须校验 sheet、表头、必需列、重复列和每行字段，并让行错误包含稳定行号与字段名。禁止遇到首个业务错误后只返回无法定位的“导入失败”。
- 同步导入必须由接口或配置明确最大文件字节数和最大行数；在上限内且契约要求原子成功时，必须在一个 transaction 中批量写入，禁止逐行查询或写入。
- 文件或行数超过同步上限、验收耗时超过 HTTP timeout、需要重试或需要进度时，HTTP handler 只保存受控 artifact 并投递 worker。Worker 写法遵循 [worker/handler.md](../worker/handler.md)，批量数据库写入遵循 [database/batch-write.md](../database/batch-write.md)。
- 临时上传文件、解析资源和 workbook reader 必须在成功与失败路径关闭并清理；原始 artifact 需要保留时必须由目标项目明确保留期、访问权限和审计，禁止默认永久保存。

## 验收

- Export 必须验证权限范围、筛选结果、固定列顺序、空数据、中文内容和临时文件清理。
- Import 必须验证超限文件、非法 workbook、缺失/重复表头、非法单元格、重复业务键、事务回滚和逐行错误定位。
- 必须通过 SQL 日志或查询计数确认导入导出不存在逐行数据库访问；异步流程必须验证重复投递和重试不会重复写入。
- 当前项目未定义 workbook 契约时只能建立上述流程边界，禁止自行确定模板字段并声称规范已经完成。
