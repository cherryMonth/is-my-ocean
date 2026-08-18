#!/usr/bin/env python3
"""Generate the original short soundtrack used by the Qixi transformation page.

The composition is intentionally rendered with only Python's standard library so
the source stays reproducible. The timeline follows the page's story:

0:00  a warm, toy-like rose motif
0:01  LOVE CORE scan and rounded armor panels begin assembling
0:03  the on-screen heart core comes online
0:07  the transformation theme gains momentum
0:15  a second emotional lift opens the final phrase
0:18  the main motif resolves into a dependable, glowing final chord
"""

from __future__ import annotations

import math
import random
import struct
import wave
from array import array
from pathlib import Path


SAMPLE_RATE = 44_100
BPM = 108
BEAT = 60 / BPM
BAR = BEAT * 4
DURATION = BAR * 8 + 3.1
SAMPLES = int(DURATION * SAMPLE_RATE)
TAU = math.tau

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "qixi-love-core.wav"

left = array("f", [0.0]) * SAMPLES
right = array("f", [0.0]) * SAMPLES
rng = random.Random(5201314)


def midi(note: int) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


def pan_gains(pan: float) -> tuple[float, float]:
    angle = (pan + 1) * math.pi / 4
    return math.cos(angle), math.sin(angle)


def adsr(t: float, duration: float, attack: float, decay: float, sustain: float, release: float) -> float:
    if t < 0 or t >= duration:
        return 0.0
    if t < attack:
        return t / max(attack, 1e-6)
    if t < attack + decay:
        return 1 - (1 - sustain) * ((t - attack) / max(decay, 1e-6))
    release_start = max(attack + decay, duration - release)
    if t < release_start:
        return sustain
    return sustain * (1 - (t - release_start) / max(duration - release_start, 1e-6))


def add_note(
    start: float,
    duration: float,
    frequency: float,
    volume: float,
    *,
    kind: str = "bell",
    pan: float = 0.0,
) -> None:
    begin = max(0, int(start * SAMPLE_RATE))
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    gl, gr = pan_gains(pan)
    phase = 0.0

    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        if kind == "bell":
            env = math.exp(-4.2 * t / max(duration, 0.1)) * min(1.0, t / 0.008)
            shimmer = 0.52 * math.sin(TAU * frequency * 2.01 * t + 0.2)
            shimmer += 0.18 * math.sin(TAU * frequency * 3.98 * t + 0.7)
            sample = math.sin(TAU * frequency * t) + shimmer
        elif kind == "pluck":
            env = math.exp(-6.3 * t / max(duration, 0.1)) * min(1.0, t / 0.004)
            sample = math.sin(TAU * frequency * t)
            sample += 0.34 * math.sin(TAU * frequency * 2 * t + 0.18)
            sample += 0.12 * math.sin(TAU * frequency * 4 * t + 0.45)
        elif kind == "bass":
            env = adsr(t, duration, 0.018, 0.09, 0.68, min(0.15, duration * 0.3))
            phase += TAU * frequency * (1 + 0.002 * math.sin(TAU * 3.2 * t)) / SAMPLE_RATE
            sample = math.sin(phase) + 0.25 * math.sin(phase * 2)
            sample = math.tanh(sample * 1.15)
        elif kind == "pulse":
            env = adsr(t, duration, 0.006, 0.04, 0.38, min(0.09, duration * 0.35))
            phase += TAU * frequency / SAMPLE_RATE
            sample = 0.72 * math.sin(phase) + 0.28 * (1 if math.sin(phase) >= 0 else -1)
        elif kind == "lead":
            env = adsr(t, duration, 0.025, 0.12, 0.74, min(0.24, duration * 0.35))
            vibrato = 1 + 0.0025 * math.sin(TAU * 5.2 * t)
            sample = 0.78 * math.sin(TAU * frequency * vibrato * t)
            sample += 0.19 * math.sin(TAU * frequency * 2 * t + 0.1)
        else:
            raise ValueError(f"Unknown note kind: {kind}")

        value = sample * env * volume
        left[index] += value * gl
        right[index] += value * gr


def add_pad(start: float, duration: float, notes: list[int], volume: float) -> None:
    for voice, note in enumerate(notes):
        frequency = midi(note)
        pan = -0.58 + voice * (1.16 / max(1, len(notes) - 1))
        gl, gr = pan_gains(pan)
        begin = int(start * SAMPLE_RATE)
        end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
        phases = [rng.random() * TAU for _ in range(3)]

        for index in range(begin, end):
            t = (index - begin) / SAMPLE_RATE
            env = adsr(t, duration, 0.72, 0.45, 0.72, 1.35)
            movement = 0.88 + 0.12 * math.sin(TAU * (0.075 + voice * 0.013) * t + voice)
            sample = 0.0
            for detune, phase in zip((-0.0042, 0.0, 0.0042), phases):
                sample += math.sin(TAU * frequency * (1 + detune) * t + phase)
            sample /= 3
            sample += 0.13 * math.sin(TAU * frequency * 2 * t)
            value = sample * env * movement * volume
            left[index] += value * gl
            right[index] += value * gr


def add_kick(start: float, volume: float = 0.45) -> None:
    duration = 0.48
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    phase = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        frequency = 46 + 105 * math.exp(-t * 28)
        phase += TAU * frequency / SAMPLE_RATE
        env = math.exp(-t * 9.8) * min(1, t / 0.002)
        click = rng.uniform(-1, 1) * math.exp(-t * 85) * 0.11
        sample = (math.sin(phase) + click) * env * volume
        left[index] += sample * 0.72
        right[index] += sample * 0.72


def add_snare(start: float, volume: float = 0.19) -> None:
    duration = 0.25
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    previous = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        noise = rng.uniform(-1, 1)
        bright = noise - previous * 0.72
        previous = noise
        env = math.exp(-t * 18) * min(1, t / 0.003)
        body = math.sin(TAU * 185 * t) * math.exp(-t * 15) * 0.32
        sample = (bright * 0.48 + body) * env * volume
        left[index] += sample * 0.68
        right[index] += sample * 0.68


def add_hat(start: float, volume: float = 0.055, pan: float = 0.0, long: bool = False) -> None:
    duration = 0.19 if long else 0.075
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    gl, gr = pan_gains(pan)
    previous = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        noise = rng.uniform(-1, 1)
        high = noise - previous
        previous = noise
        env = math.exp(-t * (21 if long else 58))
        sample = high * env * volume
        left[index] += sample * gl
        right[index] += sample * gr


def add_riser(start: float, duration: float, volume: float = 0.12) -> None:
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    phase = 0.0
    smooth_noise = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        progress = t / duration
        frequency = 180 * (8 ** progress)
        phase += TAU * frequency / SAMPLE_RATE
        smooth_noise = smooth_noise * 0.84 + rng.uniform(-1, 1) * 0.16
        env = (progress**1.65) * min(1, (duration - t) / 0.035)
        sample = (0.58 * math.sin(phase) + 0.42 * smooth_noise) * env * volume
        pan = math.sin(progress * math.pi * 3) * 0.62
        gl, gr = pan_gains(pan)
        left[index] += sample * gl
        right[index] += sample * gr


def add_servo(start: float, base: float, pan: float) -> None:
    duration = 0.31
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + duration) * SAMPLE_RATE))
    gl, gr = pan_gains(pan)
    phase = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        progress = t / duration
        frequency = base * (1 + 2.8 * progress) + 24 * math.sin(TAU * 19 * t)
        phase += TAU * frequency / SAMPLE_RATE
        env = math.sin(math.pi * progress) ** 1.5
        sample = (math.sin(phase) + 0.22 * math.sin(phase * 2.03)) * env * 0.055
        left[index] += sample * gl
        right[index] += sample * gr


def add_core_impact(start: float) -> None:
    add_kick(start, 0.7)
    for note, pan in ((65, -0.42), (69, 0.0), (72, 0.42), (76, 0.1)):
        add_note(start, 2.8, midi(note), 0.055, kind="bell", pan=pan)
    begin = int(start * SAMPLE_RATE)
    end = min(SAMPLES, int((start + 1.3) * SAMPLE_RATE))
    phase = 0.0
    for index in range(begin, end):
        t = (index - begin) / SAMPLE_RATE
        phase += TAU * (72 - 27 * t) / SAMPLE_RATE
        env = math.exp(-t * 4.1)
        sample = math.sin(phase) * env * 0.18
        left[index] += sample * 0.72
        right[index] += sample * 0.72


def beat_time(bar: int, beat: float = 0) -> float:
    return bar * BAR + beat * BEAT


# Warm harmonic foundation: Fmaj9 → Bbmaj7 → Dm9 → Cadd9, then a confident return.
pad_chords = [
    [53, 57, 60, 64, 67],
    [46, 53, 57, 60, 65],
    [50, 53, 57, 60, 64],
    [48, 55, 60, 62, 67],
    [53, 57, 60, 64, 67],
    [46, 53, 57, 60, 65],
    [50, 53, 57, 60, 64],
    [53, 57, 60, 62, 67],
]
for bar, chord in enumerate(pad_chords):
    add_pad(beat_time(bar), BAR + 0.72, chord, 0.021 if bar < 2 else 0.026)

# The memorable "rose code": A–C–F–E–C, answered by a tiny upward sparkle.
motif = [(69, 0.0, 0.65), (72, 0.75, 0.42), (77, 1.25, 0.82), (76, 2.25, 0.46), (72, 2.8, 0.75)]
for note, beat, length in motif:
    add_note(beat_time(0, beat), length * BEAT, midi(note), 0.082, kind="bell", pan=-0.22 + beat * 0.11)
for note, beat, length in ((69, 0, 0.55), (72, 0.7, 0.4), (77, 1.2, 0.6), (79, 2.0, 0.45), (81, 2.55, 0.8)):
    add_note(beat_time(1, beat), length * BEAT, midi(note), 0.076, kind="bell", pan=0.3 - beat * 0.1)

# A compact assembly sequence is locked to the page's 2.75-second armor reveal.
add_riser(0.62, 2.12, 0.09)
for cue in (
    (0.78, 280, -0.72),
    (1.12, 340, 0.72),
    (1.48, 410, -0.56),
    (1.86, 500, 0.56),
    (2.22, 610, -0.32),
):
    add_servo(*cue)
for hit in (0.82, 1.38, 1.94, 2.5):
    add_kick(hit, 0.21)
add_core_impact(2.75)

# Rose boot scan and energy gathering.
add_riser(beat_time(1, 2.7), BAR * 1.3, 0.105)
for step in range(16):
    chord = [62, 65, 69, 72, 76]
    note = chord[step % len(chord)]
    add_note(beat_time(2, step / 4), BEAT * 0.3, midi(note), 0.036, kind="pluck", pan=-0.65 + (step % 5) * 0.32)

# Rounded armor panels extend from hand → shoulders → chest → legs.
for bar in range(3, 7):
    root = [48, 53, 46, 50][bar - 3]
    for beat in range(4):
        add_kick(beat_time(bar, beat), 0.33 if bar == 3 else 0.42)
        if beat in (1, 3):
            add_snare(beat_time(bar, beat), 0.14 if bar == 3 else 0.19)
        add_note(beat_time(bar, beat), BEAT * 0.7, midi(root), 0.115, kind="bass")
        if bar >= 4 and beat in (0, 2):
            add_note(beat_time(bar, beat + 0.5), BEAT * 0.36, midi(root + 7), 0.05, kind="pulse", pan=0.2)
    for half in range(8):
        add_hat(beat_time(bar, half / 2), 0.038 + bar * 0.003, pan=-0.35 if half % 2 else 0.35, long=half == 7)

servo_cues = [
    (beat_time(3, 0.18), 260, -0.72),
    (beat_time(3, 1.18), 310, 0.72),
    (beat_time(4, 0.15), 360, -0.58),
    (beat_time(4, 1.12), 420, 0.58),
    (beat_time(4, 2.12), 490, -0.42),
    (beat_time(5, 0.15), 560, 0.42),
    (beat_time(5, 2.1), 640, -0.25),
]
for cue in servo_cues:
    add_servo(*cue)

# Transformation melody: the rose code returns stronger and brighter.
lead_lines = {
    3: [(69, 0), (72, 0.75), (77, 1.25), (76, 2.25), (72, 2.8)],
    4: [(69, 0), (72, 0.5), (77, 1), (79, 1.75), (81, 2.5), (79, 3.25)],
    5: [(77, 0), (79, 0.75), (81, 1.5), (84, 2.25), (81, 3.05)],
}
for bar, line in lead_lines.items():
    for idx, (note, beat) in enumerate(line):
        next_beat = line[idx + 1][1] if idx + 1 < len(line) else 3.85
        add_note(beat_time(bar, beat), max(0.22, (next_beat - beat) * BEAT), midi(note), 0.052, kind="lead", pan=-0.28 + idx * 0.13)

# A half-bar breath makes the final heart-core ignition feel larger.
for step in range(8):
    note = [62, 65, 69, 72][step % 4]
    add_note(beat_time(6, step / 4), BEAT * 0.28, midi(note), 0.04 + step * 0.004, kind="pluck", pan=-0.7 + step * 0.2)
add_riser(beat_time(6, 1.65), BEAT * 2.3, 0.16)
add_core_impact(beat_time(7))

# Final signature: safe, bright, and resolved rather than aggressively triumphant.
for note, beat, length, pan in (
    (77, 0.0, 0.72, -0.35),
    (84, 0.75, 0.55, 0.35),
    (81, 1.35, 0.55, -0.12),
    (79, 2.0, 0.48, 0.18),
    (77, 2.55, 2.5, 0.0),
):
    add_note(beat_time(7, beat), length * BEAT, midi(note), 0.085, kind="lead", pan=pan)

# Soft ping-pong echoes create space without washing out the mechanical timing.
dry_left = array("f", left)
dry_right = array("f", right)
for delay_seconds, amount in ((BEAT * 0.75, 0.19), (BEAT * 1.5, 0.10)):
    delay = int(delay_seconds * SAMPLE_RATE)
    for index in range(delay, SAMPLES):
        left[index] += dry_right[index - delay] * amount
        right[index] += dry_left[index - delay] * amount

# Fade edges, normalize, and write a 16-bit stereo master.
fade_in = int(0.035 * SAMPLE_RATE)
fade_out = int(2.2 * SAMPLE_RATE)
peak = 1e-9
for index in range(SAMPLES):
    edge = 1.0
    if index < fade_in:
        edge *= index / fade_in
    if index > SAMPLES - fade_out:
        edge *= (SAMPLES - index) / fade_out
    left[index] *= edge
    right[index] *= edge
    peak = max(peak, abs(left[index]), abs(right[index]))

gain = 0.89 / peak
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUTPUT), "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    chunk = bytearray()
    for l_sample, r_sample in zip(left, right):
        chunk.extend(struct.pack("<hh", int(max(-1, min(1, l_sample * gain)) * 32767), int(max(-1, min(1, r_sample * gain)) * 32767)))
        if len(chunk) >= 65_536:
            wav.writeframesraw(chunk)
            chunk.clear()
    if chunk:
        wav.writeframesraw(chunk)

print(f"Wrote {OUTPUT} ({DURATION:.2f}s)")
