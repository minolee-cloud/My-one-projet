"""rose-jjondeugi-match.wav 생성: 같은 왈츠 멜로디를 1막은 우아하게(하프, 현악, 플루트), 2막은 귀엽게(실로폰, 우쿨렐레, 피치카토)."""
import wave

import numpy as np

SR = 44100
T = 30.0
ACT2, BEAT2 = 15.5, 0.3   # index.html 과 같아야 한다
BEAT1, START1 = 0.62, 0.3
rng = np.random.default_rng(11)
out = np.zeros(int(SR * T))


def add(sig, at, gain=1.0):
    i = int(at * SR)
    j = min(len(out), i + len(sig))
    if j > i:
        out[i:j] += gain * sig[: j - i]


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(dur, a=0.005, r=0.05):
    t = tt(dur)
    return np.clip(np.minimum(t / a, (dur - t) / r), 0, 1)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, "same")


NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)


def pluck(f, dur, damp=0.996, bright=1.0):
    """카플러스-스트롱 현 뜯는 소리 (주기 단위로 벡터화)."""
    n = max(2, int(SR / f))
    total = int(dur * SR)
    y = np.zeros(total + n + 1)
    y[: n + 1] = lowpass(rng.uniform(-1, 1, n + 1), max(1, int(3 / bright)))
    i = n + 1
    while i < len(y):
        j = min(len(y), i + n)
        y[i:j] = damp * 0.5 * (y[i - n:j - n] + y[i - n - 1:j - n - 1])
        i = j
    return y[n + 1:] * env(dur, 0.002, 0.05)


def flute(f, dur):
    t = tt(dur)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5 * t) * np.clip(t / 0.3, 0, 1)
    ph = np.cumsum(2 * np.pi * f * vib / SR)
    breath = lowpass(rng.standard_normal(len(t)), 6) * 0.04
    return (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph) + breath) * env(dur, 0.09, 0.25)


def strings(freqs, dur):
    t = tt(dur)
    sig = np.zeros(len(t))
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            ph = 2 * np.pi * f * (1 + det) * t + rng.uniform(0, 6)
            sig += 2 * ((ph / (2 * np.pi)) % 1) - 1   # 톱니파
    return lowpass(sig, 18) * env(dur, 0.5, 0.6) / (3 * len(freqs))


def glock(f, dur=0.9):
    t = tt(dur)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 12)) * np.exp(-t * 4) * env(dur, 0.001, 0.05)


MELODY = [(76, 2), (74, 1), (72, 2), (67, 1), (69, 1), (72, 1), (77, 1), (76, 3),
          (74, 2), (72, 1), (71, 2), (67, 1), (69, 1), (71, 1), (74, 1), (72, 3)]
CHORDS = [(48, 52, 55), (45, 48, 52), (41, 45, 48), (48, 52, 55), (43, 47, 50), (40, 43, 47), (43, 47, 53), (48, 52, 55)]

# ---------- 1막: 우아한 왈츠 ----------
for bar, ch in enumerate(CHORDS):
    t0 = START1 + bar * 3 * BEAT1
    add(strings([NOTE(n + 12) for n in ch], 3 * BEAT1 + 0.6), t0, 0.22)
    add(pluck(NOTE(ch[0]), 2.5, 0.998, 0.6), t0, 0.35)            # 하프 베이스
    for k, n in enumerate((ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[2] + 12)):  # 하프 아르페지오
        add(pluck(NOTE(n), 2.0, 0.997, 0.8), t0 + BEAT1 * (1 + k * 0.5), 0.18)
t0 = START1
for n, d in MELODY:
    if t0 > 0.9:  # 처음 한 마디는 하프만
        add(flute(NOTE(n), d * BEAT1 * 0.98), t0, 0.16)
    t0 += d * BEAT1

# 12.3초 꽃잎이 내려앉을 때 하프 글리산도, 14초 반짝임
for k, n in enumerate(range(60, 96, 2)):
    add(pluck(NOTE(n), 1.5, 0.996, 1.2), 11.9 + k * 0.025, 0.1)
for k, n in enumerate((84, 88, 91, 96)):
    add(glock(NOTE(n), 1.5), 13.7 + k * 0.08, 0.06)

# ---------- 전환: 띵! ----------
add(glock(NOTE(96), 1.5), ACT2, 0.25)
add(glock(NOTE(103), 1.2), ACT2 + 0.04, 0.12)

# ---------- 2막: 귀여운 같은 멜로디 두 번 ----------
for rep in range(2):
    base = ACT2 + 0.05 + rep * 24 * BEAT2
    for bar, ch in enumerate(CHORDS):
        t0 = base + bar * 3 * BEAT2
        add(pluck(NOTE(ch[0]), 0.35, 0.99, 0.5), t0, 0.45)       # 피치카토 베이스
        for b in (1, 2):                                        # 우쿨렐레 짠짠
            for k, n in enumerate(sorted(n + 24 for n in ch)):
                add(pluck(NOTE(n), 0.4, 0.993, 1.0), t0 + b * BEAT2 + k * 0.012, 0.13)
        for b in range(3):                                      # 쉐이커
            add(lowpass(rng.standard_normal(int(0.04 * SR)), 2) * env(0.04, 0.002, 0.03), t0 + b * BEAT2 + BEAT2 / 2, 0.04)
    t0 = base
    for n, d in MELODY:
        add(glock(NOTE(n + 12), 0.9), t0, 0.2)
        if rep == 1:
            add(flute(NOTE(n + 12), d * BEAT2 * 0.9) * 0.7, t0, 0.07)   # 두 번째는 휘파람이 같이
        t0 += d * BEAT2

# 17.9~21.4초: 돌돌 말리는 동안 미끄럼 휘파람
t = tt(3.5)
f = 500 + 700 * (t / 3.5) ** 1.5 + 30 * np.sin(2 * np.pi * 3 * t)
add(np.sin(np.cumsum(2 * np.pi * f / SR)) * env(3.5, 0.5, 0.3), 17.9, 0.06)
# 21.4초 뿅 + 반짝
add(np.sin(np.cumsum(2 * np.pi * np.linspace(400, 1500, int(0.15 * SR)) / SR)) * env(0.15, 0.003, 0.03), 21.4, 0.25)
for k, n in enumerate((84, 88, 91, 96)):
    add(glock(NOTE(n), 1.0), 21.45 + k * 0.05, 0.1)
# 27.3초 냠! (바삭 + 뽁)
for k in range(4):
    add(lowpass(rng.standard_normal(int(0.04 * SR)), 2) * np.exp(-tt(0.04) * 60), 27.3 + k * 0.02, 0.35)
add(np.sin(np.cumsum(2 * np.pi * np.linspace(900, 300, int(0.12 * SR)) / SR)) * env(0.12, 0.002, 0.04), 27.32, 0.3)
# 28.6초 마무리 반짝
for k, n in enumerate((72, 76, 79, 84, 88, 91, 96)):
    add(glock(NOTE(n), 1.4), 28.6 + k * 0.05, 0.08)

fade = np.clip((T - np.arange(len(out)) / SR) / 0.5, 0, 1)
out = np.tanh(out * fade * 1.1)
out = (out / np.abs(out).max() * 0.9 * 32767).astype(np.int16)
with wave.open("rose-jjondeugi-match.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print("rose-jjondeugi-match.wav", len(out) / SR, "s")
