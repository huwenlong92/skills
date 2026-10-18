# Migration Plan V1

适用于离线迁移计划生成和复核。必须绑定目标身份、Git Commit、Migration ID/哈希、History/Snapshot 指纹、Normalizer 版本及风险。Plan Hash 必须排除自身与展示时间，对规范化语义 JSON 做 SHA-256。禁止生成 SQL 执行入口。任何前置条件变化必须失效。

完成标准：相同语义哈希稳定，篡改与证据不完整阻断执行准备。
