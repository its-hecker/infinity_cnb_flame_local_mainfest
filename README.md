# Project Infinity-X 4.1 / Android 17 for Pixel 4 (Flame)

This **gcam-experimental-flame** branch adds the original Google-signed Camera
**8.7.250.494820638.44** base and nine common feature splits, using the same
payload as the Coral GCam experiment. A full experimental ROM build and Flame
GCam testing are still required.

| Source path | Repository | Branch |
| --- | --- | --- |
| `device/google/coral` | [Shared device tree](https://github.com/its-hecker/infinity_cnb_android_device_google_coral/tree/gcam-experimental-flame) | `gcam-experimental-flame` |
| `vendor/google/flame` | [Flame vendor](https://github.com/its-hecker/infinityx_cnb_vendor_google_flame/tree/gcam-experimental-flame) | `gcam-experimental-flame` |
| `.repo/local_manifests` | [Flame local manifest](https://github.com/its-hecker/infinity_cnb_flame_local_mainfest/tree/gcam-experimental-flame) | `gcam-experimental-flame` |
| `kernel/google/msm-4.14` | [Shared floral kernel](https://github.com/its-hecker/infinity_cnb_kernel_google_msm-4.14/tree/cnb-Latest-stable) | `cnb-Latest-stable` |

The manifest also selects the existing ElmyraService `lineage-24.0` and Lunaris
Dolby `main` sources. The shared device checkout must stay at
**device/google/coral**; Flame's product selects its own board and vendor.

## Build

Follow [GCAM_EXPERIMENTAL.md](docs/GCAM_EXPERIMENTAL.md) for switching an existing
Flame checkout, making a fresh checkout, testing, and returning to the tested
baseline. Use Linux ROM build dependencies, Git LFS, and a persistent Byobu/Tmux
session on ServerHive.

Once this manifest and its sources have been synced, build from the source root:

```bash
bash .repo/local_manifests/build-gcam.sh
```

The helper verifies the pinned Camera APKs, selects `lineage_flame-userdebug`,
applies the existing protobuf and guarded Face framework fixes, checks Flame
vendor provenance, and builds SELinux policy and the ROM. It preserves the
server's RBE/Ninja configuration. Confirm the summary reports Flame and the
intended Infinity-X 4.1 version. Outputs go to `out/target/product/flame/`.

## Tested baseline and experiment scope

The baseline `main` manifest selects `infinity-4.1-flame` device/vendor
branches. Face ID removal, re-enrollment, unlock and crypto authentication,
plus Motion Sense/glow/Air DJ, were tested on that build.

These experimental branches inherit that work and retain Flame's camera HAL,
PixelCameraServicesFlame, camera configuration, Soli firmware, radio and Active
Edge calibration. The Google Camera package, revocable permission grants and
package-specific certificate policy are added. Aperture is omitted from the
Flame product; GoogleCameraFlame is the bundled camera. No kernel or Face/Motion
runtime changes are needed.

The integrated Face ID and Motion Sense implementation is retained; the
standalone `floral-3D-faceid-plugin` and `floral-motionsense-plugin` are not used.
Vendor `tools/flame-port-provenance.json` and its checks are inherited.
The stable Flame and Coral branches, Coral's GCam experiment, and repository
defaults are unchanged.

CI checks original Google signatures and every installed APK's bytes, device
wiring and the inherited Face/Motion source checks. It does not build or run the
full Android ROM. Test the camera modes and repeat Face/Motion tests after
flashing before considering promotion.
