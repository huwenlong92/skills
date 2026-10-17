---
name: vab-admin-display-model
description: Vab Admin 列表与详情的嵌套展示模型及其与 options 数据的职责边界
---

# 展示模型规范

本文适用于前端消费后端列表、详情、关联对象和 options 数据。

## 后端展示模型

- 前端页面必须消费后端返回的关联对象，禁止为新功能新增扁平关联展示字段依赖。
- 关联资源必须以嵌套对象读取，例如 `row.group?.name`、`row.group?.code`。
- 不新增 `xxx_name`、`xxx_code`、`xxx_status` 这类扁平展示字段依赖。
- 后端展示模型字段不足时必须调整列表或详情接口返回结构；只有接口不在本次任务范围且用户确认兼容方案时，才允许前端临时转换，并必须标注移除条件。

## 关联展示和 options 数据

- 列表页和详情页展示关联资源时必须消费后端返回的嵌套对象。
- 列表页禁止为了显示关联名称请求 options；展示模型必须由列表或详情接口一次返回。
- 列表接口、详情接口和 options 接口职责分开：列表/详情负责当前页面展示模型，options 只服务选择组件和轻量枚举输入。

远程 options 的组件加载、loaded、loading、pending、label resolver 和刷新契约以 [remote-options.md](../components/remote-options.md) 为唯一权威，本文禁止复制第二套实现规则。

## 验收

- 必须检查新代码通过嵌套对象读取关联名称、编码和状态，没有新增 `xxx_name`、`xxx_code` 一类扁平依赖。
- 必须检查列表与详情没有为了展示关联名称而请求 options。
- 涉及远程 options 时必须继续通过 [remote-options.md](../components/remote-options.md) 验收。
