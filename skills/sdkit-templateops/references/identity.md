# Identity V1
适用范围：模板发现、来源核验、遗留项目补录、多模板挂载。涉及身份文件时必须读取。

项目根目录允许 `.sdkit/template.json`；禁止在 Skill 安装目录或个人配置中保存项目身份。schema_version=1，project.repository 标识业务仓库；templates[] 每项必须有唯一 mount_id、template_id、repository、project_path、variant、origin、adopted_baseline、last_synced、ownership、tracking、adaptation。
- origin.method 可为 github-template/manual-copy/unknown；origin.status 为 verified/declared/inferred/unknown。仅验证真实来源 Commit、项目映射和来源证据后可设 verified。
- adopted_baseline 与 origin 独立：事后采纳不能伪造创建历史。未知来源不得 Apply。
- tracking 为 active/paused/detached；adaptation 为 pristine/customized/diverged/unknown。
- ownership.include/exclude 为项目路径相对 glob，exclude 优先；默认 unknown。规范化路径，拒绝越界、符号链接和大小写碰撞；多 mount 实际文件交叉时停止自动修改。
- last_synced 只能引用完成约定 Git 交付且已验证的项目内容；PR 候选不得提前更新。
正例：backend mount 使用 apps/api，frontend mount 使用 apps/web，分别绑定经核验的 Commit。
反例：仅凭 go.mod 或 src/pages 推断 sdbase-go/nuxt 来源并标 verified。
完成标准：每个 mount 均有证据等级、文件所有权、已验证 SHA 或 unknown 停止原因。
