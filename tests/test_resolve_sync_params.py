import importlib.util
import unittest
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "resolve_sync_params.py"
    spec = importlib.util.spec_from_file_location("resolve_sync_params", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load resolve_sync_params module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResolveImagesTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_maps_source_to_expected_target(self):
        result = self.module.resolve_images(
            source_image="vllm/vllm-openai:nightly",
            registry_host="registry.cn-hangzhou.aliyuncs.com",
            namespace="dslab",
        )
        self.assertEqual(result["source_ref"], "docker.io/vllm/vllm-openai:nightly")
        self.assertEqual(
            result["target_ref"],
            "registry.cn-hangzhou.aliyuncs.com/dslab/vllm-openai:nightly",
        )

    def test_defaults_tag_to_latest(self):
        result = self.module.resolve_images(
            source_image="nginx",
            registry_host="registry.cn-hangzhou.aliyuncs.com",
            namespace="dslab",
        )
        self.assertEqual(result["source_ref"], "docker.io/nginx:latest")
        self.assertEqual(
            result["target_ref"],
            "registry.cn-hangzhou.aliyuncs.com/dslab/nginx:latest",
        )

    def test_target_repository_override(self):
        result = self.module.resolve_images(
            source_image="vllm/vllm-openai:nightly",
            registry_host="registry.cn-hangzhou.aliyuncs.com",
            namespace="dslab",
            target_repository="custom-repo",
            target_tag="release",
        )
        self.assertEqual(
            result["target_ref"],
            "registry.cn-hangzhou.aliyuncs.com/dslab/custom-repo:release",
        )

    def test_rejects_invalid_source_image(self):
        with self.assertRaises(ValueError):
            self.module.resolve_images(
                source_image="",
                registry_host="registry.cn-hangzhou.aliyuncs.com",
                namespace="dslab",
            )


if __name__ == "__main__":
    unittest.main()
