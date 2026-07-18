"""Generate generic per-scene explainer narration WAVs with Kokoro.

After its model files are cached, Kokoro-82M inference runs locally without a
network connection. This template writes one 24 kHz WAV per scene plus a
``durations.json`` manifest from which composition timing can be derived.

Replace every placeholder in ``SCENE_NARRATIONS`` before running. Budget
approximately 2.55 words/second at speed 1.1. Spell out or space acronyms as
needed for pronunciation; on-screen text can retain its normal spelling.
"""

import json
from pathlib import Path

import numpy as np
import soundfile
from kokoro import KPipeline

OUTPUT_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "production" / "assets" / "audio"
)
SAMPLE_RATE_HZ = 24_000
VOICE_NAME = "af_heart"
SPEECH_SPEED = 1.1

# Explainer arc: hook → context → steps 1..3 → what it means → recap.
SCENE_NARRATIONS: list[tuple[str, str]] = [
    (
        "s1_hook",
        "How does Delta V turn a raw flow packet into a queryable record? "
        "Three steps, one pipeline — starting at the network edge.",
    ),
    (
        "s2_context",
        "Every flow — Netflow five and nine, I P Fix, s Flow — rides the "
        "same three step pipeline: the Minion listens, the gateway routes, "
        "the enricher makes sense of it. Kafka connects the stages.",
    ),
    (
        "s3_step1",
        "Step one, the Minion. One U D P port, four seven two nine, receives "
        "all four flow protocols. A four byte version sniff tells them apart; "
        "nothing else is parsed.",
    ),
    (
        "s4_step2",
        "Step two, the gateway. Each protocol streams over its own g R P C "
        "method, and lands on its own Kafka topic, keyed by location and "
        "Minion I D.",
    ),
    (
        "s5_step3",
        "Step three, the flow enricher. One Spring Cloud Stream binding "
        "consumes all four topics, parses each protocol, adds node context, "
        "and publishes enriched flows back to Kafka — ClickHouse's own "
        "consumer ingests them.",
    ),
    (
        "s6_meaning",
        "The payoff: the coupling is content blind — only the enricher "
        "understands flows. And scaling is pure Kafka: four partitions per "
        "topic, and consumer groups spread them — enricher replicas and "
        "ClickHouse's consumer threads alike.",
    ),
    (
        "s7_recap",
        "So: the Minion sniffs, the gateway routes, Kafka carries, the "
        "enricher parses and enriches, and ClickHouse answers the queries. "
        "Delta V flows, explained.",
    ),
]


def synthesize_scene(pipeline: KPipeline, scene_id: str, narration_text: str) -> float:
    """Synthesize one scene's narration; return its duration in seconds."""
    narration_text = narration_text.strip()
    if not narration_text:
        raise ValueError(f"narration is empty for {scene_id}")
    if narration_text.startswith("<") and narration_text.endswith(">"):
        raise ValueError(f"replace the narration placeholder for {scene_id}")

    audio_chunks = [
        chunk_audio
        for _graphemes, _phonemes, chunk_audio in pipeline(
            narration_text, voice=VOICE_NAME, speed=SPEECH_SPEED
        )
    ]
    if not audio_chunks:
        raise RuntimeError(f"Kokoro produced no audio for {scene_id}")

    scene_audio = np.concatenate([np.asarray(chunk) for chunk in audio_chunks])
    output_path = OUTPUT_DIRECTORY / f"{scene_id}.wav"
    soundfile.write(output_path, scene_audio, SAMPLE_RATE_HZ)
    duration_seconds = len(scene_audio) / SAMPLE_RATE_HZ
    print(f"{scene_id}: {duration_seconds:.2f}s -> {output_path.name}")
    return duration_seconds


def main() -> None:
    """Generate all scene WAVs and the durations manifest."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    scene_durations = {
        scene_id: synthesize_scene(pipeline, scene_id, narration_text)
        for scene_id, narration_text in SCENE_NARRATIONS
    }
    manifest_path = OUTPUT_DIRECTORY / "durations.json"
    manifest_path.write_text(
        json.dumps(scene_durations, indent=2) + "\n", encoding="utf-8"
    )
    total_seconds = sum(scene_durations.values())
    print(f"total narration: {total_seconds:.2f}s -> {manifest_path}")


if __name__ == "__main__":
    main()
