---
name: npmops-public-page
description: 私有源码与公开介绍页分离时，按白名单同步 README 和 demo 图片的流程。
---

# GitHub 公开介绍页

适用范围：只向独立 GitHub 介绍页同步公开 README 和图片，保留私有源码。修改脚本或真实同步前必须读取；普通 npm 发布不要求启用。

必须先按[仓库协作](repository.md)分别核验源码和公开目标身份与关联 PR。公开页仍使用本文件规定的临时 clone，禁止清空已有 checkout。

## 前置条件与放置

- 必须确认源包、公开目标仓库与分支、白名单及本次写入授权。目标必须专用于介绍页，禁止把源码仓库当目标清空。
- origin 与 repository 必须保持真实源码来源，homepage 允许指向公开页；禁止为同步修改源码 remote。
- 脚本必须放在包根目录 deploy/release/sync-github-public，Makefile 只调用它；禁止放进消费项目或重复维护发布脚本。[模板](templates/deploy/release/sync-github-public)必须审计后使用。
- GITHUB_PUBLIC_REPO_URL 必须由项目或用户提供，GITHUB_PUBLIC_BRANCH 默认 main，项目声明其他分支时才替换。缺地址必须在 clone 前停止，禁止试连占位仓库。

## 白名单与同步

- 只允许 README.public.md → README.md 和 docs/public/images/ → docs/images/；仅当前者图片目录不存在且项目明确沿用旧布局时，允许 docs/assets/ 作为图片来源。
- 禁止复制 src、playground、package.json、锁文件、内部脚本或私密配置。公开来源必须人工审查，禁止通过符号链接引入白名单外内容。
- 必须 clone 到本次创建的临时目录，只在该临时 clone 中清空除 .git 外的顶层内容，禁止清空已有 checkout。删除旧内容必须列入预览。
- 必须先用 DRY_RUN=1 make sync-github-public 预览全部增删改；dry-run 只允许 clone 和本地准备，禁止 commit/push。发现非预期文件或删除时必须停止。
- 真实同步必须有本次目标写入与 commit/push 授权，再执行 make sync-github-public；禁止从 npm 发布授权推导公开仓库写入授权。
- 必须显式暂存 README、图片与核对过的删除路径，禁止 git add .、git add -A、git commit .、强推与修改 remote。推送失败必须报告准确状态，禁止声称已同步。

```make
sync-github-public:
	bash deploy/release/sync-github-public

publish-readme: sync-github-public
```

正向形态：临时 clone 中清理旧内容，复制白名单，预览后仅提交公开文件和核对的删除。反例：清空源码 checkout 或复制整个 docs。

## 完成标准

- 修改脚本必须执行 bash -n，并在本地临时 Git 仓库验证白名单、删除预览、dry-run 不推进远端与真实同步；禁止用真实远端测试。
- 目标只有公开 README 和允许图片，源 checkout 不变，目标与删除范围符合授权。
- 人工审查文案、截图秘密与旧图片 fallback；分别报告预览、commit、push 状态，禁止用本地 commit 替代远端验收。
