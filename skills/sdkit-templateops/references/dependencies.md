# Dependencies V1
适用范围：依赖和锁文件漂移、模板依赖升级。涉及依赖升级计划时必须读取。

核验 package.json 与 package-lock.json/pnpm-lock.yaml/yarn.lock、.npmrc；go.mod/go.sum；Cargo.toml/Cargo.lock；pyproject.toml/uv.lock；pubspec.yaml/pubspec.lock。区分直接/间接、模板/业务、运行时/工具链及安全/破坏性更新。
依赖声明和锁文件必须同基线比对，锁文件漂移为 TE-2002；破坏性升级为 TE-2003。禁止直接用模板锁文件覆盖业务锁文件，禁止仅凭版本范围推断已安装依赖。
正例：输出 Nuxt 依赖变化及 pnpm 锁文件影响，保留业务自定义包。
反例：复制模板 pnpm-lock.yaml 覆盖业务项目。
完成标准：输出依赖图差异、锁定状态、风险与必要验证；无法解析时标 pending。
