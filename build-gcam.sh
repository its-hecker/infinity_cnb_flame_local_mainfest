#!/usr/bin/env bash
# Build Flame with the pinned stock Google Camera experiment.
set -eo pipefail

MANIFEST_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd -- "$MANIFEST_DIR/../.." && pwd)"
cd -- "$SOURCE_ROOT"

python3 vendor/google/flame/camera/tools/prepare_camera.py --check-hashes
source build/envsetup.sh
breakfast lineage_flame-userdebug
test "$TARGET_PRODUCT" = lineage_flame
test "$TARGET_BUILD_VARIANT" = userdebug
bash "$MANIFEST_DIR/apply-build-fixes.sh"
python3 device/google/coral/faceunlock/tools/apply_framework_fixes.py --apply
python3 vendor/google/flame/tools/check_flame_port.py --device-root device/google/coral
mka -j8 selinux_policy
mka -j8 bacon
