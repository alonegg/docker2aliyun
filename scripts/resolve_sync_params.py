#!/usr/bin/env python3
"""Resolve source/target image refs for DockerHub -> Aliyun sync workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


DEFAULT_REGISTRY_HOST = "registry.cn-hangzhou.aliyuncs.com"
DEFAULT_NAMESPACE = "dslab"
DEFAULT_SOURCE_REGISTRY = "docker.io"


def _is_registry(segment: str) -> bool:
    return "." in segment or ":" in segment or segment == "localhost"


def _parse_source_image(source_image: str) -> tuple[str, str, str]:
    source = source_image.strip()
    if not source:
        raise ValueError("source_image cannot be empty")
    if "@" in source:
        raise ValueError("digest references are not supported, please provide repo[:tag]")

    parts = source.split("/")
    if len(parts) > 1 and _is_registry(parts[0]):
        source_registry = parts[0]
        repository = "/".join(parts[1:])
    else:
        source_registry = DEFAULT_SOURCE_REGISTRY
        repository = source

    if not repository or repository.startswith("/") or repository.endswith("/"):
        raise ValueError("invalid source image repository")

    last_segment = repository.rsplit("/", 1)[-1]
    if ":" in last_segment:
        base_repository, tag = repository.rsplit(":", 1)
    else:
        base_repository, tag = repository, "latest"

    if not base_repository or not tag:
        raise ValueError("invalid source image format, expected repo[:tag]")

    return source_registry, base_repository, tag


def resolve_images(
    source_image: str,
    registry_host: str,
    namespace: str,
    target_repository: str = "",
    target_tag: str = "",
) -> dict[str, str]:
    if not registry_host or not registry_host.strip():
        raise ValueError("registry_host cannot be empty")
    if not namespace or not namespace.strip():
        raise ValueError("namespace cannot be empty")

    source_registry, source_repository, source_tag = _parse_source_image(source_image)

    resolved_target_repository = target_repository.strip() or source_repository.rsplit("/", 1)[-1]
    resolved_target_tag = target_tag.strip() or source_tag

    if ":" in resolved_target_repository or "@" in resolved_target_repository:
        raise ValueError("target_repository must not contain tag or digest")
    if "/" in resolved_target_repository:
        raise ValueError("target_repository should be repository name only")

    source_ref = f"{source_registry}/{source_repository}:{source_tag}"
    target_ref = f"{registry_host.strip()}/{namespace.strip()}/{resolved_target_repository}:{resolved_target_tag}"

    return {
        "source_ref": source_ref,
        "target_ref": target_ref,
        "registry_host": registry_host.strip(),
        "namespace": namespace.strip(),
        "target_repository": resolved_target_repository,
        "target_tag": resolved_target_tag,
        "target_console_ref": f"{namespace.strip()}/{resolved_target_repository}:{resolved_target_tag}",
    }


def _write_github_output(path: str, values: dict[str, str]) -> None:
    if not path:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve container image sync parameters")
    parser.add_argument("--source-image", required=True, help="Source image repo[:tag]")
    parser.add_argument(
        "--registry-host",
        default=os.environ.get("REGISTRY_HOST", DEFAULT_REGISTRY_HOST),
        help="Target registry host",
    )
    parser.add_argument(
        "--namespace",
        default=os.environ.get("NAMESPACE", DEFAULT_NAMESPACE),
        help="Target namespace",
    )
    parser.add_argument("--target-repository", default="", help="Target repository name override")
    parser.add_argument("--target-tag", default="", help="Target tag override")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = resolve_images(
        source_image=args.source_image,
        registry_host=args.registry_host,
        namespace=args.namespace,
        target_repository=args.target_repository,
        target_tag=args.target_tag,
    )

    _write_github_output(os.environ.get("GITHUB_OUTPUT", ""), result)
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
