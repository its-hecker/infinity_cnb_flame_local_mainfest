#!/usr/bin/env bash
# Build Flame with the pinned stock Google Camera experiment.
set -eo pipefail
trap 'build_exit_code=$?; printf "Flame build stopped at line %s (exit %s).\n" "$LINENO" "$build_exit_code" >&2' ERR

MANIFEST_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd -- "$MANIFEST_DIR/../.." && pwd)"
cd -- "$SOURCE_ROOT"

echo "Verifying Google Camera payload..."
python3 vendor/google/flame/camera/tools/prepare_camera.py --check-hashes

# Android's interactive setup uses optional probes and intentional short
# pipelines (including tr /dev/urandom | head). Load it without strict shell
# options, then check setup/target status explicitly before restoring them.
echo "Loading Android build environment..."
trap - ERR
set +e +o pipefail
source build/envsetup.sh
build_env_status=$?
if (( build_env_status != 0 )); then
    echo "Android environment setup failed (exit $build_env_status)." >&2
    exit "$build_env_status"
fi

echo "Selecting lineage_flame-userdebug..."
breakfast lineage_flame-userdebug
build_target_status=$?
set -eo pipefail
trap 'build_exit_code=$?; printf "Flame build stopped at line %s (exit %s).\n" "$LINENO" "$build_exit_code" >&2' ERR
if (( build_target_status != 0 )); then
    echo "Flame target selection failed (exit $build_target_status)." >&2
    exit "$build_target_status"
fi
if [[ "${TARGET_PRODUCT:-}" != lineage_flame ||
      "${TARGET_BUILD_VARIANT:-}" != userdebug ]]; then
    echo "Expected lineage_flame/userdebug; got ${TARGET_PRODUCT:-unset}/${TARGET_BUILD_VARIANT:-unset}." >&2
    exit 1
fi

echo "Applying build fixes and verifying the Flame port..."
bash "$MANIFEST_DIR/apply-build-fixes.sh"
python3 device/google/coral/faceunlock/tools/apply_framework_fixes.py --apply
python3 vendor/google/flame/tools/check_flame_port.py --device-root device/google/coral
echo "Building Flame SELinux policy..."
mka -j8 selinux_policy
echo "Building Flame ROM..."
mka -j8 bacon
