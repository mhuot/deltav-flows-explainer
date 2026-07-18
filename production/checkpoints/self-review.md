# Self-review — explainer-v3.mp4 (2026-07-18)

v3 reframes the video as "Delta-V flows, explained": telemetryd removed
entirely (SME: not part of the Flows conversation). Scene 1 is now a
direct how-does-it-work hook, scene 2 a three-step pipeline overview,
scene 7 a clean recap with no telemetryd box, and scene 6 attributes
partition scaling to "pure Kafka" (4 partitions/topic; consumer groups
spread them — enricher replicas and ClickHouse's 4 consumer threads per
topic alike), per the SME's second reply.

v3 gate evidence: s1/s2/s6/s7 re-synthesized (total narration 78.40 s,
video 82.85 s); lint/check 0 errors, 39/39 contrast pass; scenes 1, 2, 6,
7 snapshotted and viewed (v3-at-*.png); ffprobe duration 82.880 s (+0.030
vs plan, within ±0.1); max_volume −7.5 dB; QA frames qa-v3-*.png viewed.
Composition id renamed to deltav-flows-explainer.

---

# Self-review — explainer-v2.mp4 (2026-07-18) [superseded]

v2 corrects v1 per SME feedback (SME): scene-5 narration and visuals now
show flow-enricher as an SCS processor producing enriched flows to the
`deltav-flows` Kafka topic, with ClickHouse ingesting via its own Kafka
consumer; the recap's dashed Kafka→telemetryd spur is removed and the box
relabeled "extension seat · not in the flow path". Scene 6 (partition
scaling) intentionally unchanged pending the SME's confirmation — his note
conflicts with the source doc's Scaling-ceilings section.

v2 gate evidence: only s5 narration re-synthesized (11.12 s → 14.38 s);
all timing re-derived (total 80.15 s); lint/check 0 errors, 40/40 contrast
pass; scenes 5 and 7 re-snapshotted and viewed; ffprobe duration 80.192 s
(+0.042 vs plan, within ±0.1); max_volume −5.3 dB; QA frames
qa-v2-{47,53,75,79}.png viewed — corrected topology confirmed on screen.

---

# Self-review — explainer-v1.mp4 (2026-07-17) [superseded]

## Deliverable

`production/renders/explainer-v1.mp4` — 1920×1080 @ 30 fps, H.264 + AAC,
6.0 MB, rendered by HyperFrames (`--quality high`) in 33.2 s.

## Gate evidence

| Gate | Result |
|------|--------|
| Script lock | 186 words locked in `script/script.md` before any audio/visual work; every claim maps to `research-brief.md` facts sourced from the architecture doc |
| Measured timing | Kokoro WAVs measured (72.48 s total); all scene/audio/JS timing derived from `durations.json`; the three timing surfaces agree |
| lint | 0 errors (2 advisory warnings about file size / track density — accepted for a single-file 7-scene composition) |
| check | 0 errors; 42/42 text contrast checks pass WCAG AA |
| Snapshot review | All 7 scenes viewed at late-scene times. 3 defects found and fixed: scene-2 stamp covered the BMP chip (moved below the chip grid); scene-2 bypass arc had a mid-path gap (dash array 700 < path length; raised to 2000); scene-6 caption overlapped the partition grid (rows tightened, caption moved down) |
| ffprobe | duration 76.928 s vs plan 76.90 s (+0.028 s, within ±0.1); h264 1920×1080 30/1 + aac |
| volumedetect | max_volume −4.9 dB (< 0 dB, no clipping); mean −28.9 dB |
| Frame QA | qa-{3,15,30,45,60,74}.png extracted and viewed — content matches scene plan; mid-animation frames show expected entrance states |

## Known limitations

- Narration-beat sync is derived from word-position estimates within each
  measured clip (e.g. the scene-2 stamp lands at the "all eight queues"
  estimate), not from forced alignment; spot-listening recommended.
- "Segoe UI" / "SF Mono" / "Menlo" alias to bundled Roboto / JetBrains Mono
  at render time (reported by lint) — consistent within the render.
- Music is a deterministic synthesized pad at 0.11 volume; drop `aud-music`
  from `video/index.html` and re-render for a narration-only cut.

## Sign-off note

Content is sourced solely from `deltav-telemetryd-architecture.md`. Per the
skill's non-negotiables, the subject's owner should sign off before the
video ships to customers or official channels.
