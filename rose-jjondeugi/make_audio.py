"""rose-jjondeugi.wav 생성: index.html 과 같은 24초 타임라인에 맞춘 음악과 효과음."""
import wave

import numpy as np

SR = 44100
T = 24.0
rng = np.random.default_rng(5)
out = np.zeros(int(SR * T))


def add(sig, at, gain=1.0):
    i = int(at * SR)
    j = min(len(out), i + len(sig))
    out[i:j] += gain * sig[: j - i]


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, "same")


def env(dur, a=0.005, r=0.05):
    t = tt(dur)
    return np.minimum(1, t / a) * np.minimum(1, (dur - t) / r)


def tone(f, dur, decay=3.0, harm=(1, 0.3, 0.1)):
    t = tt(dur)
    f = np.broadcast_to(f, t.shape)
    ph = np.cumsum(2 * np.pi * f / SR)
    return sum(a * np.sin((i + 1) * ph) for i, a in enumerate(harm)) * np.exp(-t * decay) * env(dur)


def voice(dur, f0, formants, breath=0.0, rough=0.0):
    """가산 합성 목소리. f0 와 포먼트 중심은 리스트를 주면 시간에 따라 변한다."""
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    track = lambda v: np.interp(k, np.linspace(0, 1, len(v)), v) if isinstance(v, (list, tuple)) else np.full(n, float(v))
    f = track(f0) * (1 + 0.02 * np.sin(2 * np.pi * 6 * k * dur))
    if rough:
        f = f * (1 + rough * lowpass(rng.standard_normal(n), 200) * 3)
    ph = np.cumsum(2 * np.pi * f / SR)
    sig = np.zeros(n)
    for h in range(1, 40):
        w = 0.2 / h + sum(g * np.exp(-((h * f - track(fc)) / bw) ** 2) for fc, bw, g in formants)
        sig += np.where(h * f < 6000, w, 0) * np.sin(h * ph) / h ** 0.5
    sig *= env(dur, 0.02, 0.08)
    if breath:
        sig += breath * lowpass(rng.standard_normal(n), 4) * env(dur, 0.02, 0.08)
    return sig / (np.abs(sig).max() + 1e-9)


def noise_burst(dur, smooth=1, decay=10.0):
    t = tt(dur)
    return lowpass(rng.standard_normal(len(t)), smooth) * np.exp(-t * decay) * env(dur, 0.002, 0.02)


def heartbeat(at, gain):
    for d, g in ((0, 1), (0.22, 0.7)):
        t = tt(0.25)
        add(np.sin(2 * np.pi * 52 * t * (1 - t)) * np.exp(-t * 18), at + d, gain * g)


NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)

# 0~3.5초: 오르골 자장가, 마지막 음이 늘어지며 음이 떨어진다
melody = [(76, 0.4), (79, 0.4), (84, 0.4), (83, 0.4), (79, 0.4), (81, 0.4), (79, 0.8)]
t0 = 0.2
for n, d in melody:
    add(tone(NOTE(n), 1.2, 3.5, (1, 0.0, 0.25, 0.0, 0.1)), t0, 0.22)
    add(tone(NOTE(n - 24), 1.2, 3, (1, 0.2)), t0, 0.06)
    t0 += d
add(tone(np.linspace(NOTE(76), NOTE(70), int(1.0 * SR)), 1.0, 2, (1, 0.0, 0.25)), 3.0, 0.2)

# 3.5초: 천둥
add(noise_burst(0.08, 1, 40), 3.5, 0.9)
add(lowpass(noise_burst(2.5, 1, 1.6), 60), 3.52, 3.0)

# 4~7초: 낮은 드론, 빨라지는 심장박동, 올라가는 비명 같은 현악
def drone(t0, dur, gain):
    t = tt(dur)
    sig = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (55, 58.3, 82.4))
    add(lowpass(sig, 80) * env(dur, 0.6, 0.6), t0, gain)


drone(3.6, 3.4, 0.07)
bt = 4.0
while bt < 6.9:
    heartbeat(bt, 0.9)
    bt += np.interp(bt, [4, 7], [0.75, 0.3])
t = tt(2.2)
f = np.linspace(400, 1700, len(t)) * (1 + 0.03 * np.sin(2 * np.pi * 7 * t))
add(lowpass(np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))), 6) * np.linspace(0, 1, len(t)) ** 2 * env(2.2, 0.1, 0.02), 4.8, 0.18)

# 7초: 펑! 뿅 → 7.6초 착지 보잉
add(lowpass(noise_burst(0.5, 1, 6), 8), 6.95, 1.2)
add(tone(np.linspace(300, 1400, int(0.25 * SR)), 0.25, 4, (1, 0.3)), 7.0, 0.35)


def boing(at, gain=0.4, f=180):
    t = tt(0.6)
    add(tone(f * (1 + 0.5 * np.exp(-t * 6) * np.sin(2 * np.pi * 14 * t)), 0.6, 5, (1, 0.4, 0.1)), at, gain)


boing(7.6)


def pluck(f, dur=0.5):
    n = int(SR / f)
    buf = rng.uniform(-1, 1, n)
    res = np.zeros(int(dur * SR))
    for i in range(len(res)):
        res[i] = buf[i % n]
        buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.996
    return res


# 7.6~11초: 귀여운 우쿨렐레풍 (쫀드기의 평화)
for i, n in enumerate([72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84]):
    add(pluck(NOTE(n), 0.45), 7.9 + i * 0.25, 0.35)
boing(9.6, 0.35, 260)

# 11초: 음악 뚝 + 전등 지지직, 다시 드론
t = tt(0.3)
add(np.sin(np.cumsum(2 * np.pi * np.linspace(800, 60, len(t)) / SR)) * env(0.3), 10.95, 0.3)
for i in range(7):
    if rng.random() < 0.7:
        tb = tt(0.05)
        add(np.sign(np.sin(2 * np.pi * 120 * tb)) * 0.6 + rng.standard_normal(len(tb)) * 0.4, 11.0 + i * 0.09, 0.15)
drone(11.2, 11.2, 0.06)

# 11.6~13초: 삐걱삐걱 다시 자라나는 소리
t = tt(1.4)
rate = 25 + 40 * np.sin(np.pi * t / 1.4)
clicks = (np.diff(np.floor(np.cumsum(rate / SR)), prepend=0) > 0).astype(float)
creak = np.convolve(clicks, np.sin(2 * np.pi * 900 * tt(0.01)) * np.exp(-tt(0.01) * 400), "same")
add(creak * env(1.4, 0.1, 0.1), 11.6, 0.5)

# 13초: 눈 번쩍 — 불협화음 일격
t = tt(1.5)
stab = sum(np.sign(np.sin(2 * np.pi * NOTE(n) * t)) for n in (48, 49, 55, 61))
add(lowpass(stab, 10) * np.exp(-t * 2.5) * env(1.5, 0.003, 0.1), 13.0, 0.12)
add(lowpass(noise_burst(0.6, 1, 5), 30), 13.0, 1.0)

# 14~15.2초: 떨리는 트레몰로 긴장
t = tt(1.3)
trem = np.sin(2 * np.pi * NOTE(62) * t) + np.sin(2 * np.pi * NOTE(63) * t)
add(trem * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 14 * t))) * np.linspace(0.2, 1, len(t)) * env(1.3, 0.05, 0.05), 14.0, 0.1)
heartbeat(14.2, 0.8)
heartbeat(14.7, 0.9)

# 15.1초: 쫀드기 비명
A = [(800, 220, 1.0), (1250, 280, 0.6)]
add(voice(0.6, [700, 950, 1000, 900], A, breath=0.2), 15.05, 0.35)

# 와구! 와구와구! 꿀꺽!
for b in (15.64, 16.64, 17.64):
    for k in range(5):
        add(lowpass(noise_burst(0.05, 1, 60), 3), b + k * 0.025 + rng.uniform(0, 0.01), 0.8)
    t = tt(0.2)
    add(np.sin(2 * np.pi * 70 * t) * np.exp(-t * 20), b, 0.8)
    for k in range(4):  # 씹는 소리
        add(lowpass(noise_burst(0.07, 1, 30), 20), b + 0.18 + k * 0.17, 0.6)
add(voice(0.35, [320, 130], [(400, 150, 1.0), (800, 250, 0.4)]), 17.85, 0.4)

# 18.5~19.5 냠냠, 19.6 꺼억~
for k in range(5):
    add(lowpass(noise_burst(0.08, 1, 25), 25), 18.5 + k * 0.2, 0.5)
add(voice(0.8, [95, 80, 70], [(500, 180, 1.0), (900, 260, 0.5)], breath=0.3, rough=0.08), 19.6, 0.7)

# 20.5~22.4초: 오르골 다시, 느리고 음이 어긋난 채로
t0 = 20.5
for n, d in melody[:5]:
    add(tone(NOTE(n) * 0.97, 1.4, 2.5, (1, 0.0, 0.25, 0.0, 0.1)), t0, 0.16)
    t0 += 0.4
heartbeat(21.0, 0.8)
heartbeat(21.8, 0.9)

# 22.4초 정적 → 22.6 THE END 쿵 → 23.2 작은 꺽
t = tt(1.0)
add(np.sin(2 * np.pi * 45 * t) * np.exp(-t * 4), 22.6, 0.9)
add(voice(0.18, [110, 90], [(500, 180, 1.0), (900, 260, 0.5)], rough=0.05), 23.2, 0.4)

out[int(22.4 * SR):int(22.6 * SR)] = 0
out = np.tanh(out * 1.2)
out = (out / np.abs(out).max() * 0.9 * 32767).astype(np.int16)
with wave.open("rose-jjondeugi.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print("rose-jjondeugi.wav", len(out) / SR, "s")
