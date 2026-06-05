# CerebraLink — html-video template

Source for the HD product-tour MP4, built with
[nexu-io/html-video](https://github.com/nexu-io/html-video) (Apache-2.0). A
single-file GSAP composition the Hyperframes engine records to MP4 via headless
Chromium + ffmpeg.

## Files
- `index.html` — composition root (1920×1080, 10 s)
- `compositions/pipeline.html` — the animated CerebraLink pipeline (GSAP timeline)
- `template.html-video.yaml` — html-video template manifest
- `gsap.min.js` — vendored locally (so the headless render needs no network)

## Render
```bash
git clone https://github.com/nexu-io/html-video && cd html-video
pnpm install && pnpm -r build
pnpm --filter @html-video/adapter-hyperframes exec playwright install chromium-headless-shell
cp -r /path/to/cerebralink/docs/assets/video/html-video-template templates/frame-cerebralink

PID=$(node packages/cli/dist/bin.js project-create --name "CerebraLink" --json | jq -r .project_id)
node packages/cli/dist/bin.js project-set-template "$PID" --template frame-cerebralink
node packages/cli/dist/bin.js project-render "$PID" --output cerebralink-explainer.mp4
```

This is what produces the README's **Product Tour** animation
(`../cerebralink-explainer.mp4`); the inline `../cerebralink-explainer.webp` is just
that MP4 transcoded with ffmpeg so it autoplays on GitHub.

> [!IMPORTANT]
> The recorder captures the page in **real time** — the GSAP timeline must
> **auto-play** (`gsap.timeline()`, not `{paused:true}`), and the animation must live
> directly in `index.html` (the CLI render does **not** inject `data-composition-src`
> compositions). `gsap.min.js` is vendored locally so the headless render needs no network.
