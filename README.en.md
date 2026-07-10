# Signet · One prompt. A whole icon set that's unmistakably *you*.

<p align="center"><a href="README.md">中文</a> · <strong>English</strong></p>

> Not another icon library. Not another AI icon generator. Signet is a **brand-identity system for icons** — say one sentence, and your whole set, from the App Store icon down to the line glyphs in your UI, looks like it came from one brand, not ten different templates.

![Signet system showcase](assets/showcase/hero-signet.png)

<p align="center">
  <img src="https://img.shields.io/badge/styles-29-c8553d.svg" />
  <img src="https://img.shields.io/badge/UI_SVGs-272-2f5ea7.svg" />
  <img src="https://img.shields.io/badge/export_targets-8-2b2622.svg" />
  <img src="https://img.shields.io/badge/Agent-Skill-d98e3a.svg" />
  <img src="https://img.shields.io/badge/License-Apache--2.0-4c8a5b.svg" />
</p>

> **Install**: tell your agent (Codex Desktop / Claude Code…) — "Install this skill: `github.com/dososo/blcaptain-signet`"

---

## Why it exists

Shipping an app from zero, icons are the first place things fall apart: the main icon comes from a designer, the feature icons get outsourced, the empty-state art is AI'd on a whim, the little glyphs in the UI are grabbed from some open-source line set — **each fine on its own, together they look like the work of ten different teams.**

Three more traps waiting downstream:

- **Recolor to your brand, and the art goes muddy.** Most icons can't survive a palette swap — change the primary and they lose focus, gray out, clash.
- **Great big, mush at 32px.** Shrink it and the silhouette collapses, the detail smears, nobody can tell what it is.
- **One master, hand-exported to 8 platforms.** iOS corner radius, Android adaptive, HarmonyOS, watch, social previews… one at a time until your wrist hurts.

The root cause: **most tools solve "draw an icon," but the hard part is "keep a whole set unmistakably the same *you*."** The first is a drawing problem. The second is an **identity problem** — the same family as logos, visual identity, and brand books.

Signet turns identity into something an AI can reproduce reliably: material, silhouette, lighting, lens, palette, and batch consistency are all frozen into **recipes and constants.** The AI doesn't freestyle — it fills your content into a verified *material world*, so the whole set comes out as one brand.

> The bet, in one line: **looking good isn't magic, it's constants you can write into code.** Type scale, whitespace, "too dark → rejected," "unreadable at 64px → fails" — hard gates, not luck.

## Not another X

| It is **not** | It **is** |
|---|---|
| ❌ Another icon asset library (still a pile after you download) | ✅ A system where every icon **shares one identity** |
| ❌ Another "type text, get an image" generator | ✅ A **middle layer**: prompt compilation + material lock + QA + multi-platform export |
| ❌ One filter slapped on everything | ✅ 29 **material worlds**, each a real physics, not a reskin |
| ❌ Quietly calling a model behind your back | ✅ Images come from **your agent's own image model**; Signet makes them coherent, usable, shippable |

## What you get

| Dimension | What's inside |
|---|---|
| **Materials** | **29 verified visual styles** (dimensional 19 / editorial 6 / flagship 1 / flat 3), each a real material physics, not a filter |
| **Palette** | An independent **5-role palette per request** (primary/secondary/tertiary/accent/detail) — swap your brand color without going muddy or losing focus |
| **UI icons** | **272 interface SVGs** (250 themed + 22 original) **plus on-demand vector generation**: not in the set? It draws a clean SVG on the spot — no hoarding |
| **Consistency** | The Juju identity lock — swap materials and it must *not* drift into a generic pet; it's the system's **stress test** |
| **Small sizes** | 64px / 32px / 16px preflight — collapsed or smeared silhouettes get rejected, not shipped |
| **Platforms** | One master exports **Web / PWA / iOS / Android / macOS / HarmonyOS / tvOS / Social** in one pass, with manifests, preview boards, and a zip |

## What makes it different

Most icon tools are "one template over everything," and it shows — same flavor wall to wall. This one isn't:

1. **29 material worlds, each its own physics** — the crackle of kiln-glazed porcelain, the loops of crochet, cloisonné wire, the shadows of layered papercut… not a new color for the icon, a new **material** for it. Same subject, different material, completely different presence — yet all one system.
2. **The trick to recoloring without going muddy** — colors aren't arbitrary hex. They're split into 5 roles (primary, dark anchor, accent…), each with a fixed job and a luminance gate. Swap your primary and the picture changes *mood*, not clarity.
3. **The Juju lock** — one white Bichon, rendered in 29 materials, must still be *him* (black eye-nose triangle, drop ears, orange scarf). **The moment he drifts into a generic pet, the visual system isn't locked yet.** Nobody else ships a consistency yardstick like this.
4. **UI icons are generated on demand, not hoarded** — no race to stockpile 1,500. If it's not in the set, the agent **draws one on the spot** with vector primitives: natively scalable, recolorable, seamless with the 250 themed glyphs.
5. **Every run is stable** — luminance thresholds, 64px readability, batch locks, edge safe-zones are all code gates. Fail and it's rejected — no betting on the model's mood today.
6. **Clean-room by origin** — copies no third party's names, prompts, images, compositions, or naming sets. Apache-2.0 at the root; third-party glyphs attributed one by one.

## The 29 styles

One system; the variable is material. **Full interactive gallery** 👉 [online Gallery](https://dososo.github.io/blcaptain-signet/docs/gallery.html) (opens right in your browser — all 29 styles).

### Dimensional · 19 (brand marks / feature icons / high-recognition objects)

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/kiln-charm.png" width="118"><br><sub>kiln-charm · kiln glaze</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cobalt-bleed.png" width="118"><br><sub>cobalt-bleed · blue-white porcelain</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/celadon-goldline.png" width="118"><br><sub>celadon-goldline · gold inlay</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/satin-porcelain.png" width="118"><br><sub>satin-porcelain · satin</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/ridge-enamel.png" width="118"><br><sub>ridge-enamel · cloisonné</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/cloison-glass.png" width="118"><br><sub>cloison-glass · hard enamel</sub></td>
    <td align="center"><img src="assets/showcase/styles/prism-layer.png" width="118"><br><sub>prism-layer · layered glass</sub></td>
    <td align="center"><img src="assets/showcase/styles/lacquer-seal.png" width="118"><br><sub>lacquer-seal · lacquer</sub></td>
    <td align="center"><img src="assets/showcase/styles/knit-craft.png" width="118"><br><sub>knit-craft · crochet</sub></td>
    <td align="center"><img src="assets/showcase/styles/felt-field.png" width="118"><br><sub>felt-field · felt</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/silk-fold.png" width="118"><br><sub>silk-fold · silk</sub></td>
    <td align="center"><img src="assets/showcase/styles/carbon-twill.png" width="118"><br><sub>carbon-twill · carbon fiber</sub></td>
    <td align="center"><img src="assets/showcase/styles/candy-gloss.png" width="118"><br><sub>candy-gloss · glossy candy</sub></td>
    <td align="center"><img src="assets/showcase/styles/soft-molded.png" width="118"><br><sub>soft-molded · matte plastic</sub></td>
    <td align="center"><img src="assets/showcase/styles/inflate-vinyl.png" width="118"><br><sub>inflate-vinyl · inflated vinyl</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/facet-solid.png" width="118"><br><sub>facet-solid · low-poly</sub></td>
    <td align="center"><img src="assets/showcase/styles/scene-block.png" width="118"><br><sub>scene-block · isometric</sub></td>
    <td align="center"><img src="assets/showcase/styles/layer-paper.png" width="118"><br><sub>layer-paper · papercut</sub></td>
    <td align="center"><img src="assets/showcase/styles/sumi-bold.png" width="118"><br><sub>sumi-bold · sumi ink</sub></td>
    <td align="center"></td>
  </tr>
</table>

### Editorial · 6 (empty states / article art / feature explainers / brand narrative)

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/pomo-splash.png" width="118"><br><sub>pomo-splash · wet-ink splash</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/brush-block.png" width="118"><br><sub>brush-block · brush blocks</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/carve-block.png" width="118"><br><sub>carve-block · woodcut</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/riso-press.png" width="118"><br><sub>riso-press · risograph</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/cyan-draft.png" width="118"><br><sub>cyan-draft · blueprint</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/styles/contour-single.png" width="118"><br><sub>contour-single · single-line</sub></td>
    <td align="center"></td><td align="center"></td><td align="center"></td><td align="center"></td>
  </tr>
</table>

### ◆ Flagship · 1　and　Flat family · 3

<table>
  <tr>
    <td align="center" width="20%"><img src="assets/showcase/styles/nacre-drift.png" width="118"><br><sub>◆ nacre-drift · iridescent nacre</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/gradient-flow.png" width="118"><br><sub>gradient-flow · gradient</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/duotone-pop.png" width="118"><br><sub>duotone-pop · duotone</sub></td>
    <td align="center" width="20%"><img src="assets/showcase/styles/geo-bauhaus.png" width="118"><br><sub>geo-bauhaus · geometric primaries</sub></td>
    <td align="center" width="20%"></td>
  </tr>
</table>

## 272 UI SVGs (a recolorable interface icon set)

![UI SVG sampler](assets/showcase/ui-svg-272.png)

**250 themed + 22 Signet-original = 272 SVGs**, all `24×24 / 2px / round / currentColor`, covering navigation, actions, status, communication, media, files, commerce, and platform marks. Not in the set? The agent **draws one on the spot** with the vector primitives in [`param_engine.py`](skills/signet/ui/param_engine.py) — no imagegen, natively scalable, recolored with a single CSS `color`.

## Juju · the identity lock

<table>
  <tr>
    <td width="50%"><img src="assets/showcase/juju-character.png" alt="Juju identity lock"></td>
    <td width="50%"><img src="assets/examples/example-contact-sheet.png" alt="Public example contact sheet"></td>
  </tr>
</table>

A white Bichon, black eye-nose triangle, drop ears, orange scarf. He's the system's **consistency stress test**: the moment one material turns him into a generic pet, a plush toy, or a random critter, the visual system isn't locked. Locked, he stays himself across all 29 materials.

## Fits / doesn't fit

**Fits**: brand app icons · full feature-icon sets · empty states and onboarding art · product visual identity · full sets of interface line icons · multi-platform icon export · any icon system that has to stay consistent over time.

**Doesn't fit** (it'll tell you, and send you elsewhere): logos / wordmarks / lettermark trademarks · editing real photos / retouching / face swaps · cloning an existing brand's icons · one-off images with no consistency need. **A tool that does everything usually does nothing well.**

## Content → material (how to pick a style)

| Your product's character | Suggested materials |
|---|---|
| Warm, handmade, lifestyle, cultural | Ceramics (kiln-charm / cobalt-bleed / celadon) · Textiles (knit / felt / silk) |
| Refined, premium, jewelry / craft | Treasury (ridge-enamel / cloison-glass / prism-layer / ◆nacre-drift) |
| Friendly, playful, consumer app | Soft-touch (candy-gloss / soft-molded / inflate-vinyl) |
| Tech, tools, productivity | Geometric (facet-solid / scene-block / cyan-draft) |
| Editorial, content, narrative | Ink & paper (sumi-bold / pomo-splash / brush-block / carve-block) |
| Modern, flat, interface graphics | Flat family (gradient-flow / duotone-pop / geo-bauhaus) |
| Just a set of line UI icons | UI SVG track — one sentence, brand-colored icon set |

## Which agents work

Not tied to any single agent. **If your agent supports Skills (can read a local skill folder), it works:**

| Agent | How |
|---|---|
| **Codex Desktop** (primary target) | Ships with [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json), uses its built-in image model |
| **Claude Code** | Drop into `~/.claude/skills/` |
| Cursor / Gemini CLI / any Skill-capable agent | Generic install |

> Images are produced by your agent's own image model; UI line icons are generated as vector code and need no image model.

## Install

```bash
# Generic (recommended): let your agent install it
npx skills add dososo/blcaptain-signet -g

# Or clone into your agent's skills folder
git clone https://github.com/dososo/blcaptain-signet.git
# Codex Desktop:  cp -R blcaptain-signet ~/.agents/skills/
# Claude Code:    cp -R blcaptain-signet ~/.claude/skills/

# To use the CLI standalone, install deps once
python -m pip install pyyaml Pillow pytest
```

## How to use (conversational, 30 seconds)

Once installed, just talk to your agent:

> **"Make my app 'FlowPilot' an icon set in `kiln-charm` (kiln-glazed ceramic), brand color `#2758D8`, export iOS / Android / HarmonyOS."**

Signet will: **show 4 quick candidates → lock the style and produce the full set → preflight small sizes → export all platforms at once.**

Not happy? Just say so: "different material / color's too dull / this one's too busy / make the icon bigger."

## Workflow: pick material → generate → ship

```text
One sentence of what you want
   ↓ infer the subject + recommend 4 candidate materials
Pick 1 material + brand color
   ↓ compile the visual contract + batch consistency lock
Your agent generates the 1024×1024 master
   ↓ preflight: silhouette / contrast / edges / 64px readability
Export Web / PWA / iOS / Android / macOS / HarmonyOS / tvOS / Social at once
```

Want it as a CLI (no agent): `build_prompt.py` (compile the prompt) · `preflight_icon_set.py` (master preflight) · `export_icon_assets.py` (multi-platform export) · `ui_pipeline.py` (brand-colored UI SVG set).

## Design principles

- **Single focus, centered, readable at 64px** — cut detail before you add complexity. If it's unclear, it doesn't pass.
- **Material bible** — each style uses only its own native material and physics; no cross-material mixing.
- **Constraint as craft** — material marks (bevels, air gaps, cloisonné wire) are generated by structure, not painted on as a surface filter.
- **Whitespace, limited color** — subject concentrated, background quiet, palette bounded; infinite choice only makes it easier to make something ugly.
- **Luminance gates** — one dark anchor, bright highlights; recolor without collapse.
- **Clean-room** — learn only public craft principles; copy no third party's assets, naming, or identity.

## Roadmap

- **UI icon expansion** — keep growing the themed high-frequency set; evaluate permissive sets like Phosphor.
- **Promoting in-progress styles** — spikes like `press-relief` (letterpress) are pushing for small-size readability; they merge once they pass.
- **Export enhancements** — track new platform specs (e.g. iOS layered `.icon`) and cover more adaptive forms.
- **More material worlds** — carefully add distinctive new materials, while keeping it all *one system*.

## FAQ

<details>
<summary><strong>Does Signet call an image model itself?</strong></summary>

No. Signet compiles prompts and visual constraints; images are produced by your agent's own image model. UI line icons are generated entirely as vector code, never through imagegen.
</details>

<details>
<summary><strong>How is this different from "download an icon library"?</strong></summary>

A library hands you a pile of ready-made icons — assembled, they still look assembled. Signet hands you *identity*: one set of material, palette, and lighting rules runs through all your icons, so recolor, resize, or re-platform, it's still the same you.
</details>

<details>
<summary><strong>Can I use only the UI SVGs, without the image styles?</strong></summary>

Yes. The UI SVG track is independent, all `currentColor`, ideal for inlining in a frontend and recoloring with CSS.
</details>

<details>
<summary><strong>Can I use it commercially?</strong></summary>

Code, docs, style recipes, and original metadata are Apache-2.0. Third-party UI glyph licenses are in [`LICENSES.md`](LICENSES.md); model-generated images are also subject to the terms of the model you use, and you're responsible for your own trademark and brand review.
</details>

## Author

Created and maintained by **爆裂队长NEXT** (BLCaptain).

- GitHub: [@dososo](https://github.com/dososo) · X: [@thinkszyg](https://x.com/thinkszyg)
- Work email: [blteam2026@outlook.com](mailto:blteam2026@outlook.com)
- Feedback: [Issues](https://github.com/dososo/blcaptain-signet/issues)

## License

Apache License 2.0. See [LICENSE](LICENSE), [NOTICE.md](NOTICE.md), and [LICENSES.md](LICENSES.md).
