# Toolchain V1
适用范围：项目、模板、CI 与实际工具链版本核验。只读检测必须读取。

Node：.node-version、.nvmrc、package.json engines/packageManager；Go：go.mod、go.work toolchain、.go-version；Rust：rust-toolchain.toml、Cargo.toml、Cargo.lock；Python：.python-version、pyproject.toml、uv.lock；Flutter：pubspec.yaml、pubspec.lock 与实际 SDK。
必须分别记录 project_declared、template_required、local_actual、ci_declared、compatibility、evidence_refs；缺失为 unknown，不能假定兼容。只读阶段不得执行会自动安装或切换工具链的命令；fnm/gvm/rustup/uv 为可选入口。
正例：Node 24 项目在本地 Node 22 下报告 TE-2001，不改变 PATH。
反例：为通过构建自动运行 rustup update 或 corepack prepare latest。
完成标准：明确每栈版本来源、差异、未验证项与停止条件。
