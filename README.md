# 🐳 DockerHub → Aliyun 镜像同步工具

一键将 DockerHub 镜像同步至阿里云容器镜像服务，基于 GitHub Actions + [crane](https://github.com/google/go-containerregistry)。

## ✨ 特性

- 🖱️ **一键触发** — GitHub Actions 页面表单输入，无需命令行
- 📦 **多架构同步** — 自动同步所有 CPU 架构（amd64/arm64 等）
- 📋 **批量支持** — 多行输入，一次同步多个镜像
- 📊 **可视化报告** — Job Summary 表格展示同步结果与拉取命令
- 🔐 **安全** — 凭据通过 GitHub Secrets 管理，不会泄露

## 🔧 前置配置

在 GitHub 仓库 **Settings → Secrets and variables → Actions** 中配置：

| Secret 名称 | 必需 | 说明 |
|---|---|---|
| `ALIYUN_USERNAME` | ✅ | 阿里云容器镜像服务用户名 |
| `ALIYUN_PASSWORD` | ✅ | 阿里云容器镜像服务密码 |
| `DOCKERHUB_USERNAME` | ⚠️ 推荐 | DockerHub 用户名（避免匿名限速） |
| `DOCKERHUB_TOKEN` | ⚠️ 推荐 | DockerHub Personal Access Token |

> **已固化配置**（无需修改）：
> - 仓库地址：`registry.cn-hangzhou.aliyuncs.com`
> - 命名空间：`dslab`

## 🚀 使用方法

### 1. 进入 Actions 页面

打开仓库 → **Actions** tab → 左侧选择 **"🐳 Sync DockerHub → Aliyun"**

### 2. 点击 "Run workflow"

在输入框中填写要同步的镜像，每行一个：

```
vllm/vllm-openai:nightly
pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
nginx:latest
```

### 3. 查看结果

Workflow 完成后，点击对应的 run → 查看 **Summary** 页面，你将看到：

| 状态 | 源镜像 | 阿里云镜像 | 拉取命令 |
|:----:|--------|-----------|----------|
| ✅ | `vllm/vllm-openai:nightly` | `dslab/vllm-openai:nightly` | `docker pull registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly` |
| ✅ | `nginx:latest` | `dslab/nginx:latest` | `docker pull registry.cn-hangzhou.aliyuncs.com/dslab/nginx:latest` |

### 4. 拉取镜像

```bash
docker pull registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly
```

## 📐 镜像名映射规则

| 源镜像 | 阿里云镜像 | 规则 |
|--------|-----------|------|
| `vllm/vllm-openai:nightly` | `dslab/vllm-openai:nightly` | 取 `/` 后的部分 |
| `nvidia/cuda:12.0-base` | `dslab/cuda:12.0-base` | 取最后一段 |
| `nginx:latest` | `dslab/nginx:latest` | 无 `/`，直接使用 |
| `nginx` | `dslab/nginx:latest` | 自动补 `:latest` |

## ❓ FAQ

**Q: workflow_dispatch 在哪里触发？**
> Actions tab → 左侧 workflow 列表 → 选择 workflow → 右上角 "Run workflow" 按钮

**Q: 同步速度如何？**
> crane 直接操作 registry API（不经过 Docker daemon），通常 1-3 分钟完成一个镜像

**Q: 支持私有镜像吗？**
> 支持。配置 `DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN` 后即可拉取私有镜像

**Q: 支持非 DockerHub 的源吗？**
> 支持。crane 兼容任何 OCI 标准仓库，输入完整地址即可，如 `ghcr.io/owner/image:tag`
