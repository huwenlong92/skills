# Three-way Diff V1
适用范围：BASE 原始模板、TARGET 目标模板、PROJECT 业务项目的比较。

必须锁定三个 Git Commit/内容证据；比较 BASE→TARGET 与 BASE→PROJECT，分类 added/deleted/modified/renamed/both_modified/configuration_changed/dependency_changed/toolchain_changed；ownership 为 template/business/mixed/unknown；risk 为 safe/review/blocked。
safe 只表示可生成候选补丁，不表示自动写入授权。相同文件双向修改、语义变化、未知所有权、重命名不确定和路径重叠必须人工审查或阻止。认证、SSR、数据库及配置语义需要技术栈规则；不以文本无冲突推断行为兼容。
正例：新增不冲突的模板文件标 safe 候选；业务自定义 Handler 标 review。
反例：模板删除文件就自动删除业务同名文件。
完成标准：每个受影响文件有三方 blob 证据、所有权、风险、理由与后续验证。
