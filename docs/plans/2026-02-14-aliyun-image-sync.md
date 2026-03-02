# DockerHub to Aliyun Sync Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a GitHub Action that lets users submit a DockerHub image/tag and sync it to Aliyun ACR with clear post-run output.

**Architecture:** Use `workflow_dispatch` inputs for user-friendly entry, a small Python resolver for validation/mapping, and `crane cp` for registry-to-registry copy. Publish the final Aliyun image URL in both Step Summary and job outputs.

**Tech Stack:** GitHub Actions YAML, Python 3 stdlib (`unittest`), shell steps, `crane` CLI.

### Task 1: Add TDD tests for input parsing and target image mapping

**Files:**
- Create: `tests/test_resolve_sync_params.py`
- Test: `tests/test_resolve_sync_params.py`

**Step 1: Write the failing test**

Add tests that import `scripts/resolve_sync_params.py` and assert:
- `vllm/vllm-openai:nightly` maps to target `registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly`
- tag defaults to `latest`
- `target_repository` override works
- invalid source image fails

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_resolve_sync_params.py -v`
Expected: FAIL with import error because resolver module does not exist yet.

### Task 2: Implement resolver script minimally to satisfy tests

**Files:**
- Create: `scripts/resolve_sync_params.py`
- Modify: `tests/test_resolve_sync_params.py`

**Step 1: Write minimal implementation**

Implement:
- `resolve_images(source_image, registry_host, namespace, target_repository="", target_tag="")`
- strict source parsing (`repo[:tag]`, optional registry)
- default tag `latest`
- default target repository basename from source repository
- computed `source_ref`, `target_ref`, and `target_console_ref`

**Step 2: Run test to verify it passes**

Run: `python -m unittest tests/test_resolve_sync_params.py -v`
Expected: PASS.

### Task 3: Add GitHub Action workflow for manual dispatch sync

**Files:**
- Create: `.github/workflows/sync-dockerhub-to-aliyun.yml`

**Step 1: Define workflow inputs**

`workflow_dispatch` inputs:
- `source_image` (required)
- `target_repository` (optional)
- `target_tag` (optional)
- `dry_run` (boolean, default false)

**Step 2: Implement workflow steps**

- Checkout code
- Resolve refs with Python script and export outputs
- Validate required secrets (`ALIYUN_USERNAME`, `ALIYUN_PASSWORD`)
- Login to DockerHub if optional credentials are provided
- Login to Aliyun registry
- Install `crane`
- If not dry run, execute `crane cp <source_ref> <target_ref>`
- Publish `target_ref` as step summary and workflow output

### Task 4: Document how users submit requests and read results

**Files:**
- Create: `README.md`

**Step 1: Write usage guide**

Include:
- prerequisites (required and optional GitHub secrets)
- how to run workflow from GitHub UI (`Run workflow`)
- recommended input pattern examples
- where sync result appears (run Summary + logs + output variable)

**Step 2: Verification commands**

Run:
- `python -m unittest tests/test_resolve_sync_params.py -v`

Expected: PASS.
