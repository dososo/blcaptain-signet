# Output Spec — per platform

Generate ONE 1024×1024 master, then `export_icon_assets.py` produces everything below.
Sizes/opacity are dictated by each platform; the script enforces them.

## Web / favicon
- PNG ladder: 16,32,48,64,96,128,180,192,256,384,512,1024.
- `favicon.ico`: multi-res 16/32/48. WebP at 192/512 for modern browsers.
- Background: usually **transparent**.

## PWA
- Icons 72–512; `manifest.json` with `icons[]`; **maskable** 192/512 (glyph inside 80%
  safe zone on a filled square). Provide `theme_color`/`background_color`.

## iOS (flat / legacy path)
- `AppIcon.appiconset` with `Contents.json`; sizes from 20pt@2x up to 1024 marketing.
- **Opaque, full-bleed, no alpha, no self-rounded corners** — the OS applies the squircle.
- If master is transparent, the script flattens onto `--ios-bg`.
- **Caveat (be honest):** a *native iOS 26 "Liquid Glass" `.icon`* file needs per-layer
  artwork assembled in Apple's **Icon Composer** and CANNOT be produced from one flat
  raster. The flat set still renders on-device (system applies its own material). This
  limit applies to ANY tool that outputs a single flat image, Signet included.

## macOS
- `.iconset` with 16→512 plus @2x. Build the `.icns` on macOS:
  `iconutil -c icns Name.iconset -o Name.icns`. (macOS still needs discrete sizes —
  no single-size auto-gen like iOS.)

## Android
- Launcher PNGs per density (mdpi 48 → xxxhdpi 192).
- **Adaptive icon**: `ic_launcher_foreground` (glyph in central 66% keyline),
  `ic_launcher_background` (solid), `mipmap-anydpi-v26/ic_launcher.xml`.
- Foreground should be transparent; background solid.

## Social / README
- `social-preview.png` 1200×630. `preview.png` contact sheet (16→256) for docs/stores.

## Format & vector notes
- Image models output raster (PNG/JPEG/WebP), **not native SVG**. `gpt-image-2` supports
  flexible sizes (1024 up to 2K/4K-class) but **no transparent background** (use
  gpt-image-1.5/1 for transparency). Signet always generates one master and produces the
  small-size ladder via local LANCZOS downscale — deterministic and auditable.
- **SVG** is offered ONLY when the art is genuinely vector-simple (flat, few colors).
  Then use an external tracer (e.g. `vtracer`/`potrace`) as an optional post-step and
  label it "auto-traced, verify manually". Never claim vector fidelity for gradient/3D art.
- **ICO/ICNS** are produced (Pillow / iconutil). WebP for web weight savings.
