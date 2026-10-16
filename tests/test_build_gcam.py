"""Exercise startup and failure handling without downloading Android sources."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "build-gcam.sh"


class BuildGcamTests(unittest.TestCase):
    def run_helper(self, **overrides):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / ".repo/local_manifests"
            manifest.mkdir(parents=True)
            shutil.copyfile(HELPER, manifest / "build-gcam.sh")
            (manifest / "apply-build-fixes.sh").write_text(
                'printf "fixes\\n" >> "$BUILD_TEST_TRACE"\n'
            )
            scripts = {
                "vendor/google/flame/camera/tools/prepare_camera.py": "camera",
                "device/google/coral/faceunlock/tools/apply_framework_fixes.py": "face",
                "vendor/google/flame/tools/check_flame_port.py": "port",
            }
            for name, event in scripts.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "import os, pathlib, sys\n"
                    f"with pathlib.Path(os.environ['BUILD_TEST_TRACE']).open('a') as f: f.write('{event}\\n')\n"
                    f"sys.exit(int(os.environ.get('BUILD_TEST_FAIL_{event.upper()}', '0')))\n"
                )
            setup = root / "build/envsetup.sh"
            setup.parent.mkdir()
            setup.write_text('''
printf 'envsetup\n' >> "$BUILD_TEST_TRACE"
if [[ "${BUILD_TEST_FAIL_SETUP:-0}" != 0 ]]; then
    return "$BUILD_TEST_FAIL_SETUP"
fi
if [[ "${BUILD_TEST_OPTIONAL_PROBE:-0}" == 1 ]]; then
    test -n "${BUILD_TEST_UNUSED:-}"
fi
# Match the intentional early-closing pipeline in Infinity's host naming.
build_test_suffix=$(tr -dc 'a-z0-9' < /dev/urandom | head -c 4)
breakfast() {
    printf 'target\n' >> "$BUILD_TEST_TRACE"
    if [[ "${BUILD_TEST_FAIL_TARGET:-0}" != 0 ]]; then
        return "$BUILD_TEST_FAIL_TARGET"
    fi
    test -n "${BUILD_TEST_UNUSED:-}"
    export TARGET_PRODUCT="${BUILD_TEST_PRODUCT:-lineage_flame}"
    export TARGET_BUILD_VARIANT=userdebug
}
mka() {
    printf '%s\n' "$*" >> "$BUILD_TEST_TRACE"
    if [[ "$*" == '-j8 selinux_policy' ]]; then
        return "${BUILD_TEST_FAIL_POLICY:-0}"
    fi
    return "${BUILD_TEST_FAIL_ROM:-0}"
}
''')
            trace = root / "events"
            env = dict(os.environ, BUILD_TEST_TRACE=str(trace), **overrides)
            result = subprocess.run(
                ["bash", str(manifest / "build-gcam.sh")], cwd=root,
                env=env, text=True, capture_output=True, timeout=15,
            )
            return result, trace.read_text().splitlines() if trace.exists() else []

    def test_interactive_setup_pipeline_and_target_probes_allow_build(self):
        result, events = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("stopped", result.stderr)
        self.assertEqual(events, ["camera", "envsetup", "target", "fixes",
                                  "face", "port", "-j8 selinux_policy", "-j8 bacon"])

    def test_optional_environment_probe_allows_build(self):
        result, events = self.run_helper(BUILD_TEST_OPTIONAL_PROBE="1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("stopped", result.stderr)
        self.assertIn("-j8 bacon", events)

    def test_real_failures_stop_before_later_steps(self):
        cases = [
            ({"BUILD_TEST_FAIL_CAMERA": "2"}, "envsetup"),
            ({"BUILD_TEST_FAIL_SETUP": "3"}, "target"),
            ({"BUILD_TEST_FAIL_TARGET": "4"}, "fixes"),
            ({"BUILD_TEST_PRODUCT": "lineage_coral"}, "fixes"),
            ({"BUILD_TEST_FAIL_FACE": "5"}, "port"),
            ({"BUILD_TEST_FAIL_POLICY": "6"}, "-j8 bacon"),
        ]
        for overrides, forbidden in cases:
            with self.subTest(overrides=overrides):
                result, events = self.run_helper(**overrides)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(forbidden, events)
                self.assertIn("failed" if "BUILD_TEST_FAIL_SETUP" in overrides or
                              "BUILD_TEST_FAIL_TARGET" in overrides else
                              "Expected" if "BUILD_TEST_PRODUCT" in overrides else
                              "stopped", result.stderr)

    def test_rom_failure_is_reported(self):
        result, events = self.run_helper(BUILD_TEST_FAIL_ROM="7")
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertEqual(events[-1], "-j8 bacon")
        self.assertIn("stopped", result.stderr)


if __name__ == "__main__":
    unittest.main()
