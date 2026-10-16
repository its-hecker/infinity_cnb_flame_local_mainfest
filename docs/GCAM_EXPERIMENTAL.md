# Stock Google Camera experiment for Flame

Preinstalls the original Google-signed **8.7.250.494820638.44** (`65822832`)
on Project Infinity-X 4.1 / Android 17 for Pixel 4. This is the same exact
base-plus-nine-split payload used by the Coral experiment. GCam operation on
Flame Android 17 still needs a complete ROM build and physical-device testing.

| Source | Branch |
| --- | --- |
| `infinity_cnb_android_device_google_coral` | `gcam-experimental-flame` |
| `infinityx_cnb_vendor_google_flame` | `gcam-experimental-flame` |
| `infinity_cnb_flame_local_mainfest` | `gcam-experimental-flame` |
| `infinity_cnb_kernel_google_msm-4.14` | `cnb-Latest-stable` |

The device checkout remains **device/google/coral**, with Flame vendor at
**vendor/google/flame**. The new branches inherit the tested Flame 3D Face ID
and Motion Sense implementation from `infinity-4.1-flame`. The camera HAL,
firmware, kernel, and existing Face/Motion runtime code are retained.
Only the Flame product selects `GoogleCameraFlame`. Aperture is omitted by setting
`PRODUCT_NO_CAMERA := true` before inheriting Infinity's common product.

## Switch an existing Flame source checkout

From your existing Flame Infinity source root:

```bash
git -C .repo/local_manifests fetch origin gcam-experimental-flame:gcam-experimental-flame &&
git -C .repo/local_manifests switch gcam-experimental-flame &&
repo sync -c -j8 --fail-fast device/google/coral vendor/google/flame &&
bash .repo/local_manifests/build-gcam.sh
```

These commands expect the Flame local-manifest repository, not Coral's
`local_manifests` repository. Fetch and switch refuse conflicting local changes.
For subsequent updates, use `git pull --ff-only` on this manifest branch
before syncing. The helper verifies the committed APK bytes, selects the Flame
userdebug product, applies the existing protobuf and guarded Face fixes, checks
the original Flame port, and builds SELinux policy and the ROM. It preserves
the provider's RBE/Ninja environment.

## New source checkout

Use the stable README's build dependencies and a persistent Byobu/Tmux session.

```bash
mkdir -p ~/infinityx-flame-gcam &&
cd ~/infinityx-flame-gcam &&
repo init -u https://github.com/ProjectInfinity-X/manifest -b 17 --git-lfs &&
git clone --branch gcam-experimental-flame --single-branch \
  https://github.com/its-hecker/infinity_cnb_flame_local_mainfest .repo/local_manifests &&
repo sync -c -j8 --fail-fast --no-clone-bundle --no-tags --optimized-fetch &&
git -C kernel/google/msm-4.14 submodule update --init --recursive &&
bash .repo/local_manifests/build-gcam.sh
```

Do not combine the Coral and Flame local manifests. Confirm the product summary
shows `lineage_flame`, `INFINITY_BUILD=flame`, and the intended Infinity 4.1
version before compiling. This branch does not relabel a newer upstream ROM.

## Verify after flashing

See `device/google/coral/camera/README.md`. Check Camera version 8.7.250,
the base plus nine split names and `google_camera_app` SELinux domain.
Test front/rear/2x photos, HDR+, Portrait, Night Sight, video/audio, slow motion,
panorama/Photo Sphere, preview and lock-screen launch. Recheck Face ID, including
removal and re-enrollment, and Motion Sense/glow/Air DJ before promotion.
Uninstall a newer Camera app's updates in Settings if /data overrides this
preinstalled version.

CI verifies source wiring, the original Google signer, all installed APK bytes
and the inherited Face/Motion provenance. It does not build or run the full ROM.

## Return to the tested Flame sources

```bash
git -C .repo/local_manifests fetch origin main:refs/remotes/origin/main &&
git -C .repo/local_manifests switch main &&
git -C .repo/local_manifests pull --ff-only &&
repo sync -c -j8 --fail-fast device/google/coral vendor/google/flame
```

If the checkout was initially cloned as a single experimental branch, create
the local main branch first with
`git -C .repo/local_manifests switch --track origin/main` instead of
`switch main`. Rebuild using the stable README's instructions. A Camera update
in /data is separate from source branch selection and can survive a dirty flash.
