---
name: vab-admin-business-options
description: Vab Admin 固定枚举、远端注册表和关联展示模型的数据来源判定
---

# 业务 options 分流

本文适用于判断状态、类型、等级、分类和其他 options 应由前端代码、远端注册表还是列表/详情展示模型提供。本文只定义数据来源；固定枚举组件读取 [enum-components.md](enum-components.md)，远端注册表组件与 store 读取 [remote-options.md](remote-options.md)。

## 唯一判定表

| 数据类型 | 可观察条件 | 必须采用 |
|---|---|---|
| 固定代码枚举 | 值集合随代码发布，后台不能新增、编辑、停用或排序 | 本地 `options.ts` 与 [enum-components.md](enum-components.md) |
| 后台可维护注册表 | 数据库中可新增、编辑、启停、删除或排序 | 版本化 options API、Pinia store 与 [remote-options.md](remote-options.md) |
| 关联资源展示 | 列表或详情行需要显示关联对象名称、编码或状态 | 当前列表/详情接口返回嵌套对象 |
| 页面局部配置 | 只控制当前页面布局、步骤或临时交互，不代表业务枚举 | 留在当前页面或组件 |

- migration 或 seed 只提供初值但后台可以维护的数据，必须判定为远端注册表。
- 值当前看起来稳定不能证明它是固定枚举；必须以后台是否允许维护为判定条件。
- 禁止把远端注册表复制为前端常量，也禁止在多个页面维护语义相同的 options。
- 禁止为了显示关联名称请求 options 再逐行匹配；展示模型必须由列表或详情接口一次返回。
- 同名状态属于不同业务状态机时必须分别保留，禁止仅因 value 相同合并。

## 变更数据来源

- 固定枚举改为后台可维护时，必须删除本地值数组，迁移到 [remote-options.md](remote-options.md) 的 API/store/component 协议，并替换全部调用方。
- 远端注册表改为代码枚举时，必须确认后台维护入口和历史动态值已经下线，才允许迁入本地 `options.ts`。
- 数据来源变更禁止保留两套并行 label 或 options 作为长期兼容；确需迁移期兼容时必须写明删除条件。

## 验收

- 每组新增或修改的 options 必须对应判定表中的一行，并能说明后台是否允许维护。
- 必须搜索页面内的 options 数组、label/type map 和逐行关联匹配，确认没有第二份数据来源。
- 固定枚举必须继续通过 [enum-components.md](enum-components.md) 验收，远端注册表必须继续通过 [remote-options.md](remote-options.md) 验收。
- 列表与详情关联展示必须继续通过 [display-model.md](../api/display-model.md) 验收。
