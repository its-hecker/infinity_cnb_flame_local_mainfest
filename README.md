# Project Infinity X 4.1 / Android 17 for Pixel 4 (flame)

Flame integration based on the tested Coral 3D Face ID and Motion Sense port.
The standalone `floral-3D-faceid-plugin` and `floral-motionsense-plugin` are not used.

| Source path | Repository | Branch |
| --- | --- | --- |
| `device/google/coral` | [Shared Coral/Flame device tree](https://github.com/its-hecker/infinity_cnb_android_device_google_coral/tree/infinity-4.1-flame) | `infinity-4.1-flame` |
| `vendor/google/flame` | [Flame vendor](https://github.com/its-hecker/infinityx_cnb_vendor_google_flame/tree/infinity-4.1-flame) | `infinity-4.1-flame` |
| `kernel/google/msm-4.14` | [Shared floral kernel](https://github.com/its-hecker/infinity_cnb_kernel_google_msm-4.14/tree/cnb-Latest-stable) | `cnb-Latest-stable` |
| `packages/apps/ElmyraService` | [Active Edge service](https://github.com/LineageOS/android_packages_apps_ElmyraService/tree/lineage-24.0) | `lineage-24.0` |
| `vendor/lunaris/dolby` | [Lunaris Dolby](https://github.com/its-hecker/vendor_lunaris_dolby) | `main` |

The device repository is shared: `lineage_flame.mk` selects the Pixel 4 board,
1080×2280 display, overlays, audio, thermal configuration and Flame vendor.
It must remain checked out at **`device/google/coral`**. Renaming that directory
to `device/google/flame` breaks its includes and module namespaces.

The kernel already uses `floral_defconfig` with `CONFIG_BOARD_FLORAL=y` and
both `sm8150-coral-*` and `sm8150-flame-*` DTBOs. No Flame kernel changes are
needed. Any future Flame-only kernel changes must use a separate branch.
The Coral stable branches and repository defaults are unchanged.

## Port contents

- The Coral legacy HIDL Face HAL, private Android 13 camera/handler ABI,
  calibration solver, thermal/Face HIDL interfaces, and direct Citadel
  Keymaster binding to `libcrypto-v33`.
- The existing guarded framework fixes for challenge revocation and enrollment
  feature mapping. These must be applied after source sync; syncing the device
  tree does not itself patch `frameworks/base`.
- The exact Coral OsloFeedback APK, GoogleParts UI, production SystemUI
  allowlist overlay, permissions, properties and SELinux policy.
- Coral's current Motion Lab/Air DJ payload and remaining Google wallpapers.
  The incompatible Pokémon Sidekick renderer is removed during packaging.
- Flame's original radio images, camera configuration, Soli firmware package,
  Active Edge calibration and other device-specific blobs are retained.

The vendor's `tools/flame-port-provenance.json` records the donor revision,
transplanted payload hashes, and unchanged Flame firmware/radio Git blobs.
Face ID and Motion Sense were tested on Coral; a complete build and phone
validation on Flame are still required. No Flame ROM ZIP is supplied here.

## New checkout

Use a separate Linux build directory so the working Coral checkout is kept.
Use a persistent Byobu/Tmux session on ServerHive. Install the ROM build
dependencies and Git LFS before syncing.

```bash
mkdir -p ~/infinityx-flame &&
cd ~/infinityx-flame &&
repo init -u https://github.com/ProjectInfinity-X/manifest -b 17 --git-lfs &&
git clone --branch main --single-branch \
    https://github.com/its-hecker/infinity_cnb_flame_local_mainfest \
    .repo/local_manifests &&
repo sync -c -j8 --fail-fast --no-clone-bundle --no-tags --optimized-fetch &&
git -C kernel/google/msm-4.14 submodule update --init --recursive
```

This manifest replaces the Coral local manifest for this checkout; do not
install both. An existing `roomservice.xml` containing any of the same five
paths must be reviewed before sync to avoid duplicate projects.
The upstream manifest branch `17` tracks the ROM sources; their version
configuration determines the reported release. Verify it is 4.1 before building.

## Build

```bash
cd ~/infinityx-flame &&
source build/envsetup.sh &&
breakfast lineage_flame-userdebug &&
test "$TARGET_PRODUCT" = lineage_flame &&
test "$TARGET_BUILD_VARIANT" = userdebug &&
bash .repo/local_manifests/apply-build-fixes.sh &&
python3 device/google/coral/faceunlock/tools/apply_framework_fixes.py --apply &&
python3 vendor/google/flame/tools/check_flame_port.py \
    --device-root device/google/coral &&
mka -j8 selinux_policy &&
mka -j8 bacon
```

Use the full `lineage_flame-userdebug` target with this Infinity lunch wrapper.
Do not use `lineage_coral` or the old three-part `lineage_flame-cp2a-userdebug`
form. Keep ServerHive's provided RBE/Soong environment; the helper only handles
the existing product-aware protobuf-provider compatibility fix.

Before compiling, the product summary should show `TARGET_PRODUCT=lineage_flame`,
`INFINITY_BUILD=flame` and an Infinity **4.1** ZIP name ending in `flame`.
If upstream changes the ROM version, choose its matching source revision before
continuing; this manifest does not relabel a newer release as 4.1.

Outputs are in `out/target/product/flame/`. Verify important payloads:

```bash
ls -lh out/target/product/flame/*.zip
ls -l out/target/product/flame/system_ext/overlay/GoogleOsloSystemUIOverlay.apk
readelf -d out/target/product/flame/vendor/bin/hw/android.hardware.biometrics.face@1.0-service.google \
    | rg 'libcamera2ndk_face|libstagefright_foundation-v33'
readelf -d out/target/product/flame/vendor/lib64/android.hardware.keymaster@4.1-impl.nos.so \
    | rg 'libcrypto-v33'
```

Reapply the guarded Face framework fixes after syncing `frameworks/base`.
An existing checkout with missing indexed files can use the inherited recovery
helper: `python3 .repo/local_manifests/tools/restore_checkout.py --restore`.

## Phone validation

After a successful Flame build and flash, check Face enrollment, repeated
unlock, opening Face settings, model removal and enrollment again. Check both
cameras, reboot, and unlock after reboot. Then test Motion Sense music gestures,
glow, Air DJ, Motion Lab training and the remaining wallpaper picker.

If either feature fails, collect `adb logcat -b all -d`, `adb logcat -b crash -d`,
`adb shell lshal`, `adb shell cmd overlay list --user 0 com.android.systemui`,
and kernel logs with `adb shell su -c dmesg` if root is available. Record which
feature and exact action failed. Packaging/CI checks do not establish phone
runtime success.
