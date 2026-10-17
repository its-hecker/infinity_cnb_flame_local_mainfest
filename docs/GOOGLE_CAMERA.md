# Stable Google Camera for Flame

The maintainer confirmed Google Camera works on Flame on **2026-10-17** and
approved promotion of the tested `gcam-experimental-flame` package to stable.
The original Google-signed **8.7.250.494820638.44** (`65822832`) base and nine
common feature splits are unchanged. Aperture is omitted from the ROM.

| Source | Stable branch |
| --- | --- |
| `infinity_cnb_android_device_google_coral` | `infinity-4.1-flame` |
| `infinityx_cnb_vendor_google_flame` | `infinity-4.1-flame` |
| `infinity_cnb_flame_local_mainfest` | `main` |
| `infinity_cnb_kernel_google_msm-4.14` | `cnb-Latest-stable` |

The shared device checkout remains **device/google/coral**, with Flame vendor
at **vendor/google/flame**. `lineage_flame.mk` selects `GoogleCameraFlame` and
sets `PRODUCT_NO_CAMERA := true` before Infinity's common product is inherited.
PixelCameraServicesFlame, camera HAL/configuration, Face ID and Motion Sense are
retained. This promotion does not change the Coral stable branches or defaults.

## Switch the existing Flame GCam checkout to stable

Run in the existing persistent Byobu/Tmux session after any build has finished:

```bash
cd ~/infinityx-flame-gcam &&
git -C .repo/local_manifests fetch origin main:refs/remotes/origin/main &&
if git -C .repo/local_manifests show-ref --verify --quiet refs/heads/main; then
    git -C .repo/local_manifests switch main
else
    git -C .repo/local_manifests switch --no-track -c main refs/remotes/origin/main
fi &&
git -C .repo/local_manifests pull --ff-only origin main &&
repo sync -c -j8 --fail-fast device/google/coral vendor/google/flame &&
git -C kernel/google/msm-4.14 submodule update --init --recursive &&
bash .repo/local_manifests/build-gcam.sh
```

A single-branch experimental clone does not automatically recognise `origin/main`
for branch guessing. These commands create local `main` explicitly with
`--no-track` when needed and pull from `origin main` explicitly, without changing
the existing fetch configuration. Conflicting local edits cause Git/Repo to stop
for review. The two selected projects contain this promotion; existing
local Soong/header changes and the build output directory are retained.

## New checkout

Use Linux ROM build dependencies, Git LFS and a persistent Byobu/Tmux session:

```bash
mkdir -p ~/infinityx-flame &&
cd ~/infinityx-flame &&
git lfs install &&
repo init -u https://github.com/ProjectInfinity-X/manifest -b 17 --git-lfs &&
git clone --branch main --single-branch \
    https://github.com/its-hecker/infinity_cnb_flame_local_mainfest \
    .repo/local_manifests &&
repo sync -c -j8 --fail-fast --no-clone-bundle --no-tags --optimized-fetch &&
git -C kernel/google/msm-4.14 submodule update --init --recursive &&
bash .repo/local_manifests/build-gcam.sh
```

Keep this Flame manifest separate from the Coral local manifest. The helper
verifies the pinned Camera APK bytes, selects `lineage_flame-userdebug`, applies
the existing protobuf and guarded Face fixes, checks Flame vendor provenance,
and builds SELinux policy followed by the ROM. Keep ServerHive's RBE/Ninja
environment. Verify `TARGET_PRODUCT=lineage_flame`, `INFINITY_BUILD=flame` and
the intended ROM version in the product summary. ZIPs go to
`out/target/product/flame/`.

If a checkout is missing indexed files or the root Trusty copy, recover them:

```bash
python3 .repo/local_manifests/tools/restore_checkout.py --restore &&
repo sync -l -j1 --fail-fast build/make trusty/vendor/google/aosp kernel/google/msm-4.14 &&
git -C kernel/google/msm-4.14 submodule update --init --recursive &&
cmp trusty/vendor/google/aosp/lk_inc.mk lk_inc.mk
```

## Verify after flashing

See `device/google/coral/camera/README.md` for Camera version, split and process
domain checks. On a clean installation, Aperture should have no package path:

```bash
adb shell dumpsys package com.google.android.GoogleCamera
adb shell ps -AZ | grep com.google.android.GoogleCamera
adb shell pm path org.lineageos.aperture
```

For future changes, test front/rear/2x photos, HDR+, Portrait, Night Sight,
video/audio, slow motion, panorama/Photo Sphere, preview and lock-screen launch.
Recheck Face ID removal, re-enrollment and unlock, plus Motion Sense/glow/Air DJ.
A newer installed Camera update in /data may override the bundled version.

CI checks original Google signatures and installed APK bytes, device wiring,
manifest/build startup/recovery, and the existing Face/Motion provenance.
