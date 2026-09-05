---
name: vab-admin-app-upload
description: Vab Admin 业务上传组件、AppUpload 凭据协议和自定义上传模式
---

# AppUpload 使用说明

本文适用于新增或修改文件上传、上传凭据、删除文件和上传模式。`AppUpload` 是后台文件上传的统一组件；只有业务交互或上传协议无法通过其 props、slots、request adapters 或 handlers 表达时，才允许单独实现上传底座。

## 业务上传组件

页面需要上传时必须定义当前业务上传组件并复用 `AppUpload`；只有调用一次且不需要业务默认值或适配逻辑时，才允许在页面中直接使用 `AppUpload`。

- 不要在页面表单里直接写原生 `input type="file"`。
- 不要在页面里手写上传进度、分片、预签名 URL、删除等流程。
- 普通业务上传封装成页面组件或模块组件，例如 `components/upload/index.vue`、`components/avatar-upload/index.vue`。
- 多页面复用后再提升为模块组件或全局 `App*` 组件。
- 业务上传组件只负责业务默认值、accept、path、credential-request、delete-request、预览形态和额外参数。
- 真实上传行为仍交给 `AppUpload` 和后端凭证接口。
- 改用业务上传组件后，必须删除页面里旧的 `input type="file"` 和手写上传逻辑。

## 基础用法

未传 `credential-request` 时，组件使用 `src/api/system/file.ts` 中的项目通用上传接口：

```vue
<AppUpload v-model:value="logo" path="website" :accept="['.png', '.jpg', '.jpeg', '.svg', '.ico']">
  <template #child>
    <img v-if="logo" :src="logo" />
  </template>
</AppUpload>
```

`path` 会传给后端凭证接口，用于决定上传目录或业务分类。

## 使用已定义的业务接口

如果业务已经在 `src/api/**` 中定义了自己的上传凭证接口，直接通过 `credential-request` 传入方法：

```vue
<script setup lang="ts">
import { getAvatarUploadCredential } from '/@/api/account/user'
</script>

<template>
  <AppUpload v-model:value="avatar" path="avatar" :credential-request="getAvatarUploadCredential" />
</template>
```

业务接口入参需要接收上传组件传入的数据，返回值需要是上传凭证：

```ts
import request from '/@/utils/request'
import type { UploadCredentialPayload, UploadCredentialResult } from '/@/plugins/AppUpload/types'

export function getAvatarUploadCredential(data: UploadCredentialPayload): Promise<UploadCredentialResult> {
  return request({
    url: '/account/avatar/upload',
    method: 'PUT',
    data,
  }) as Promise<UploadCredentialResult>
}
```

如果已有 API 返回值外层包了 `data`，在页面里包一层适配：

```ts
const getUploadCredential = async (data: UploadCredentialPayload) => {
  const res = await getAvatarUploadCredential(data)
  return res.data
}
```

然后传给组件：

```vue
<AppUpload v-model:value="avatar" path="avatar" :credential-request="getUploadCredential" />
```

## 传递额外参数

业务接口需要额外参数时，通过 `upload-data` 传入。组件会和文件信息一起传给 `credential-request`：

```vue
<AppUpload
  v-model:value="avatar"
  path="avatar"
  :upload-data="{ scene: 'avatar', max_size: 2097152 }"
  :credential-request="getAvatarUploadCredential"
/>
```

最终凭证请求会包含：

- `path`
- `name`
- `size`
- `last_modified`
- `upload-data` 中的额外字段

## 上传凭证结构

后端凭证接口必须返回 `mode`，前端只按 `mode` 分发上传方式，不根据 URL 字段反推：

```ts
interface UploadCredentialResult {
  mode: 'local_chunk' | 'direct_put' | 'multipart_put' | string
  upload_id?: string
  upload_url?: string
  upload_urls?: string[]
  complete_url?: string
  chunk_size: number
  path: string
}
```

内置模式：

- `local_chunk`：上传分片到应用接口
- `direct_put`：使用单个预签名 URL 上传完整文件
- `multipart_put`：使用多个预签名 URL 上传分片，并调用完成合并 URL

## 自定义上传模式

如果业务接口返回新的 `mode`，页面通过 `handlers` 注册对应处理器：

```vue
<script setup lang="ts">
import { getAvatarUploadCredential } from '/@/api/account/user'
import type { UploadModeContext } from '/@/plugins/AppUpload/types'

async function uploadAvatar(context: UploadModeContext) {
  // context.file 原始文件
  // context.credential 后端凭证
  // context.setLoaded(value) 更新进度
}
</script>

<template>
  <AppUpload
    v-model:value="avatar"
    path="avatar"
    :credential-request="getAvatarUploadCredential"
    :handlers="{ avatar_upload: uploadAvatar }"
  />
</template>
```

自定义 handler 只处理自己的上传动作。上传完成后，组件统一使用凭证返回的 `path` 更新 `v-model:value`。

## 删除接口

未传 `delete-request` 时使用 `src/api/system/file.ts` 中的项目通用删除函数。业务有独立删除接口时通过 `delete-request` 传入：

```vue
<AppUpload v-model:value="avatar" path="avatar" :delete-request="deleteAvatarFile" />
```

删除接口入参固定为：

```ts
{ path: string }
```

## 验收

- 必须检查页面没有新增原生文件 input、上传分片、进度、预签名或删除流程。
- 必须验证凭据按 `mode` 分发，未知 mode 明确失败，禁止根据 URL 字段猜测模式。
- 使用业务凭据或删除接口时，必须验证 adapter 的输入输出符合 `AppUpload` 契约。
- 重构完成后必须确认旧上传状态、旧请求和旧样式已经删除，并人工检查上传、进度、成功回填、失败和删除流程。
