"""laugh-loop.wav 생성: index.html 과 같은 16초 타임라인에 맞춘 웃음소리/효과음."""
import wave

import numpy as np

SR = 44100
T = 16.0
rng = np.random.default_rng(3)
out = np.zeros(int(SR * T))


def add(sig, at):
    i = int(at * SR)
    j = min(len(out), i + len(sig))
    out[i:j] += sig[: j - i]


def voice(dur, f0, formants, amp=1.0, breath=0.0):
    """가산 합성 목소리. f0 와 formants 는 (시작, 끝) 또는 상수."""
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    track = lambda v: np.interp(k, np.linspace(0, 1, len(v)), v) if isinstance(v, (list, tuple)) else np.full(n, v)
    f = track(f0) * (1 + 0.01 * np.sin(2 * np.pi * 6 * k * dur))
    phase = np.cumsum(2 * np.pi * f / SR)
    sig = np.zeros(n)
    for h in range(1, 40):
        fh = h * f
        weight = 0.25 / h
        for fc, bw, g in formants:
            fc = track(fc)
            weight = weight + g * np.exp(-((fh - fc) / bw) ** 2)
        sig += np.where(fh < 6000, weight, 0) * np.sin(h * phase) / h ** 0.5
    env = np.minimum(1, k * dur / 0.012) * np.minimum(1, (1 - k) * dur / 0.04)
    sig = sig * env
    if breath:
        noise = np.convolve(rng.standard_normal(n), np.ones(6) / 6, "same")
        sig += breath * noise * env
    return amp * sig / (np.abs(sig).max() + 1e-9)


A = [(800, 220, 1.0), (1250, 280, 0.6)]  # "아"
I = [(320, 150, 1.0), (2300, 400, 0.6)]  # "이"
O = [(450, 150, 1.0), (850, 250, 0.6)]   # "오"


def ha(at, f0, loud):
    add(0.12 * loud * rng.standard_normal(int(0.035 * SR)) * np.linspace(0.2, 1, int(0.035 * SR)), at)
    dur = rng.uniform(0.11, 0.16)
    add(voice(dur, (f0 * 1.08, f0 * 0.92), A, amp=0.55 * loud, breath=0.15), at + 0.03)


def laugh_section(t0, t1, level, pitch):
    t = t0
    count = 0
    while t < t1:
        L = level(t)
        f0 = pitch(t) * rng.uniform(0.95, 1.08) * (1 + 0.15 * L)
        ha(t, f0, 0.35 + 0.65 * L)
        count += 1
        gap = np.interp(L, [0, 1], [0.42, 0.14]) * rng.uniform(0.85, 1.15)
        if L > 0.8 and count % 7 == 0:  # 숨넘어가는 흡기음
            add(voice(0.3, (pitch(t) * 3.2, pitch(t) * 4), I, amp=0.25, breath=0.6), t + gap)
            gap += 0.35
        t += gap


def build_level(t):
    if t < 6:
        k = (t - 1) / 5
        return 0.1 + 0.9 * k * k
    if t < 10.2:
        return 1.0
    k = (t - 10.2) / 3.8
    return min(1.0, 0.1 + 0.9 * k * k)


def smooth(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1)
    return k * k * (3 - 2 * k)


DOG, CAT = 210, 430
# 강아지 웃음 1~6초, 변신 중엔 목소리가 고양이 쪽으로, 8.2초에 뚝
laugh_section(1.0, 8.15, build_level, lambda t: DOG + (CAT - DOG) * smooth(6, 7.5, t))
# 고양이 웃음 10.2~14초, 변신 중 강아지 목소리로, 15.5초에 뚝
laugh_section(10.4, 15.45, build_level, lambda t: CAT + (DOG - CAT) * smooth(14, 15.5, t))


def whoosh(at, dur, up=True):
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    noise = np.convolve(rng.standard_normal(n), np.ones(12) / 12, "same")
    f = 250 + 1400 * k ** 2 if up else 1650 - 1400 * k ** 2
    sweep = np.sin(np.cumsum(2 * np.pi * f / SR))
    env = np.sin(np.pi * k) ** 1.5
    add(0.35 * env * (0.7 * noise + 0.3 * sweep), at)


def chime(at):
    for i, f in enumerate([1568, 2093, 2637, 3136]):
        n = int(0.9 * SR)
        k = np.arange(n) / SR
        add(0.12 * np.sin(2 * np.pi * f * k) * np.exp(-k * 5), at + i * 0.06)


whoosh(6.0, 1.5, up=True)
chime(7.4)
whoosh(14.0, 1.5, up=False)
chime(15.4)

# 정색: "야옹." 후 귀뚜라미
add(voice(0.6, [480, 720, 620, 430], [([320, 800, 800, 450], 200, 1.0), ([2300, 1250, 1200, 850], 300, 0.6)], amp=0.6), 8.45)
for i in range(6):
    t = 9.35 + (i // 3) * 0.45 + (i % 3) * 0.07
    n = int(0.045 * SR)
    k = np.arange(n) / SR
    add(0.08 * np.sin(2 * np.pi * 4600 * k) * np.sin(np.pi * k / k[-1]), t)

# 정색: "멍."
add(voice(0.22, (190, 130), O, amp=0.7, breath=0.1), 15.55)

out = np.tanh(out * 1.4)
out = (out / np.abs(out).max() * 0.9 * 32767).astype(np.int16)
with wave.open("laugh-loop.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print("laugh-loop.wav", len(out) / SR, "s")
