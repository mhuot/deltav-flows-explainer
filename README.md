# Delta-V flows — explainer video

An 85-second narrated explainer of how flow telemetry ingestion works in
Delta-V: Minion → minion-gateway → Kafka → flow-enricher → Kafka →
ClickHouse. The entire video is source code: every scene, word, color, and
timing is a small edit followed by a ~30-second re-render.

**Watch:** [`production/renders/explainer-v4.mp4`](production/renders/explainer-v4.mp4)

## How it was made

Produced with the
[mhuot/explainer-video-skill](https://github.com/mhuot/explainer-video-skill)
workflow (Kokoro TTS + HyperFrames + FFmpeg, fully local after setup).
That repo documents the method, toolchain installation, composition rules,
and production gates; this repo is one video produced by it.

## Repo layout

```
production/
  research/research-brief.md      # every scripted claim, source-mapped; SME corrections
  proposal.md                     # narrative arc, scene list, theme
  script/script.md                # locked narration (v1→v4 revision history)
  scene_plan/scene-plan.md        # derived timing table + per-scene visual notes
  checkpoints/decision-log.json   # append-only production decisions
  checkpoints/self-review.md      # post-render QA evidence (all versions)
  checkpoints/snapshots|frames/   # reviewed stills
  assets/audio/                   # Kokoro WAVs + durations.json
  renders/explainer-v4.mp4        # the deliverable
tools/tts_generate.py             # narration synthesis (edit SCENE_NARRATIONS)
video/index.html                  # THE VIDEO — 7 scenes, one GSAP timeline
video/assets/                     # vendored gsap + scene audio
```

## Updating the video

Prerequisites (Node ≥ 22, bun, FFmpeg with libx264, a HyperFrames build,
Python 3.12 + Kokoro) are covered by the skill repo's
[environment bootstrap](https://github.com/mhuot/explainer-video-skill).
Below, `CLI` means `node "$HYPERFRAMES_DIR/packages/cli/dist/cli.js"`.

**The one rule that governs everything:** the script locks first, and every
timing number downstream is *derived from measured narration audio* — never
guessed. If you change any words, you must re-measure and re-derive.

### Changing the script (narration)

1. Edit `SCENE_NARRATIONS` in `tools/tts_generate.py`. Write acronyms
   spaced for the TTS ("U D P", "g R P C"); on-screen text keeps real
   spelling. Budget ≈2.55 words/second.
2. Synthesize and measure:

   ```bash
   uv venv --python 3.12 .venv
   uv pip install --python .venv/bin/python "kokoro>=0.9.4,<1" numpy soundfile
   PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python tools/tts_generate.py
   ```

   This writes one WAV per scene plus
   `production/assets/audio/durations.json` with measured durations.
3. Re-derive the timing table (see
   `production/scene_plan/scene-plan.md` for the current one):

   ```
   n_start[0]     = 0.5                       # first narration starts at 0.5 s
   n_start[i+1]   = n_start[i] + dur[i] + 0.5 # 0.4–0.6 s breathing gap
   scene_start[i] = n_start[i] - 0.3          # visuals lead narration slightly
   TOTAL          = last n_end + ~0.9         # fade-out room
   ```

4. Apply the derived numbers to **all three timing surfaces** in
   `video/index.html` — they must agree exactly:
   - each `<section>`'s `data-start` / `data-duration`
   - each `<audio>`'s `data-start` / `data-duration`
   - the JS scene constants (`S1`…`S7`) and the root `data-duration`

   Also nudge any GSAP beats inside the changed scene so callouts land on
   the new narration phrasing.
5. Regenerate the music bed at the new length (`TOTAL`, fade at
   `TOTAL − 3.5`) — the exact FFmpeg `aevalsrc` recipe is in the skill
   docs — then copy audio into the composition:

   ```bash
   cp production/assets/audio/*.wav video/assets/audio/
   ```

### Changing visuals only

Edit `video/index.html` directly — no audio or timing work needed. Theme
lives in the `:root` CSS variables (one accent color); scene layouts are
plain absolutely-positioned HTML/SVG. Respect the composition rules from
the skill docs, chiefly: entrances are GSAP `fromTo` (never CSS transform
initial states), timed elements need `class="clip"`, media elements keep
explicit unique `id`s, and animate only transforms/opacity (+
`strokeDashoffset` for SVG edge draws).

### Validate, render, QA (every change)

```bash
cd video
$CLI lint                      # structural rules
$CLI check                     # runtime, layout, WCAG AA contrast
$CLI snapshot --at <seconds>   # then actually LOOK at the changed scenes
$CLI render --quality high --output ../production/renders/explainer.mp4

ffprobe -show_entries format=duration ../production/renders/explainer.mp4
ffmpeg -i ../production/renders/explainer.mp4 -af volumedetect -f null -
```

Pass criteria: 0 lint/check errors, duration within ±0.1 s of the derived
`TOTAL`, `max_volume` below 0 dB, and extracted frames matching the scene
plan. Record what you verified in `production/checkpoints/self-review.md`,
and log any decision changes in `production/checkpoints/decision-log.json`
(append-only). The skill repo documents the full gate discipline.

## Version history

- **v4** — recap ends on persistence: "…every flow is persisted in
  ClickHouse, to answer queries later."
- **v3** — reframed as "Delta-V flows, explained" per SME direction: the
  vestigial telemetryd daemon is out of scope for the Flows conversation
  and no longer appears; scaling is attributed to pure Kafka (4 partitions
  per topic; consumer groups spread them — enricher replicas and
  ClickHouse's consumer threads alike).
- **v2** — corrected per SME review: flow-enricher is a Spring Cloud Stream
  *processor* (consumes raw-flow topics, produces enriched flows to the
  `deltav-flows` Kafka topic; ClickHouse ingests it with its own Kafka
  consumer).
- **v1** — superseded; not included in this repo.
