# History Evidence V1

适用于离线 History/Attempt 证据封装。必须校验环境、方言、范围、来源 Commit、History 与 Snapshot 指纹、采集器及时间。自称 verified 的 JSON 不构成可信认证，V1 一律视为未认证输入，禁止输出可执行 Ready。失败或未知 Attempt 必须阻断。禁止连接数据库。

完成标准：无可信外部证明时不得提升信任等级。

V1 仅验证证据封装字段格式，不验证采集器真实性、签名、数据库状态或证据新鲜度。即使输入字段声明 verified，也不能赋予执行权限。
