# DockerHub 镜像同步到阿里云 ACR（GitHub Action）

这个仓库提供一个手动触发的 GitHub Action，把 DockerHub 镜像同步到阿里云 ACR。

示例：  
`vllm/vllm-openai:nightly` -> `registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly`

## 1. 前置配置

在 GitHub 仓库 `Settings -> Secrets and variables -> Actions` 中配置：

| 名称 | 必需 | 说明 |
| --- | --- | --- |
| `ALIYUN_USERNAME` | 是 | 阿里云容器镜像服务用户名 |
| `ALIYUN_PASSWORD` | 是 | 阿里云容器镜像服务密码 |
| `DOCKERHUB_USERNAME` | 否（推荐） | DockerHub 用户名（私有仓库/限流场景推荐） |
| `DOCKERHUB_TOKEN` | 否（推荐） | DockerHub Personal Access Token |

固定参数已在 workflow 内置：
- `REGISTRY_HOST=registry.cn-hangzhou.aliyuncs.com`
- `NAMESPACE=dslab`

## 2. 用户如何优雅输入同步需求

### 方式 A：GitHub Web UI（推荐）

1. 打开 `Actions` 页面。
2. 选择工作流 `Sync DockerHub Image to Aliyun ACR`。
3. 点击 `Run workflow`，填写参数：
- `source_image`（必填）：DockerHub 镜像，格式 `repo[:tag]`，如 `vllm/vllm-openai:nightly`
- `target_repository`（可选）：目标仓库名覆盖，默认取源镜像最后一段（`vllm-openai`）
- `target_tag`（可选）：目标 tag 覆盖，默认等于源 tag
- `dry_run`（可选）：先预览，不执行复制

### 方式 B：GitHub CLI

```bash
gh workflow run sync-dockerhub-to-aliyun.yml \
  -f source_image="vllm/vllm-openai:nightly" \
  -f target_repository="" \
  -f target_tag="" \
  -f dry_run=false
```

## 3. Action 完成后如何展示同步地址

工作流会在 `Run summary` 输出一张结果表，包含：
- Source Image
- Target Image
- Aliyun Console Ref
- Status

其中 `Target Image` 就是你需要复制/分发的最终地址，例如：

`registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly`

## 4. 推荐使用流程

1. 先用 `dry_run=true` 验证映射结果是否符合预期。
2. 再用 `dry_run=false` 执行实际同步。
3. 在 `Run summary` 复制最终目标地址。
