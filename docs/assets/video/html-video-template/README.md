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
node packages/cli/dist/bin.js project-render "$PID" --output cerebralink-tour.mp4
```

> [!NOTE]
> The README's inline tour (`../cerebralink-tour.webp`) is an ffmpeg crossfade
> montage of the repo's diagram SVGs — it renders inline on GitHub. Use html-video
> when you want a polished HD MP4 to attach to a release or PR (GitHub does not play
> a committed MP4 inline in the README).
