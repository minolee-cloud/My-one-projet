"""쫀드기 그림 만들기: 주황-노랑-주황 줄무늬, 가로 결, 설탕 알갱이, (구우면) 그을음.

strip.png         갓 꺼낸 쫀드기 한 줄 (말리는 장면, 쫀드기 장미)
strip-grilled.png 구운 쫀드기 한 줄 (구운 쫀드기 카드)
closeup.png       구운 쫀드기를 아주 가까이서 본 모습 (꽃잎과 나란히 보는 장면)
"""
import numpy as np
from PIL import Image, ImageFilter

ORANGE = np.array([238, 104, 38], np.float32)
YELLOW = np.array([246, 198, 42], np.float32)


def stretched_noise(rng, h, w, sx, sy):
    """가로로 길게 늘인 노이즈 → 쫀드기의 결."""
    small = rng.standard_normal((max(2, h // sy), max(2, w // sx))).astype(np.float32)
    small = (small - small.min()) / (small.max() - small.min()) * 255
    return np.asarray(Image.fromarray(small.astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255 - 0.5


def make_strip(w, h, seed, grill=0.0, char_top=0.0):
    rng = np.random.default_rng(seed)
    y = (np.arange(h) / h)[:, None]
    # 위 주황 / 가운데 노랑 / 아래 주황, 경계는 살짝 번지고 물결친다
    wave = stretched_noise(rng, 1, w, 60, 1)[0] * 0.05
    top, bot = 0.34 + wave, 0.63 - wave * 0.8
    soft = 0.025
    yel = 1 / (1 + np.exp(-(y - top) / soft)) * (1 - 1 / (1 + np.exp(-(y - bot) / soft)))
    img = ORANGE * (1 - yel[..., None]) + YELLOW * yel[..., None]
    # 가로 결 (굵은 결 + 가는 결)
    fib = stretched_noise(rng, h, w, 40, 2) * 0.22 + stretched_noise(rng, h, w, 12, 1) * 0.14
    rows = 0.5 + 0.5 * np.sin(np.arange(h) / h * np.pi * h / 3.5)  # 촘촘한 줄 결
    fib += (rows[:, None] - 0.5) * 0.12 * (0.6 + stretched_noise(rng, h, w, 8, 1))
    img *= (1 + fib)[..., None]
    # 오돌토돌한 표면과 설탕 알갱이 반짝임
    img *= (1 + rng.normal(0, 0.05, (h, w)))[..., None]
    sugar = (rng.random((h, w)) > 0.993).astype(np.float32)
    sugar = np.asarray(Image.fromarray((sugar * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
    img = img * (1 - sugar[..., None] * 2) + 255 * sugar[..., None] * 2
    # 윗면 윤기
    img += (40 * np.exp(-((y - 0.18) / 0.08) ** 2))[..., None]
    if grill > 0:
        # 결을 따라 길게 그을린 자국과 가장자리 탄 부분
        burn = np.clip(stretched_noise(rng, h, w, 80, 6) * 3 - 0.35, 0, 1)
        burn += np.clip(stretched_noise(rng, h, w, 25, 3) * 3 - 0.9, 0, 1)
        edge = np.exp(-(y / 0.06)) + np.exp(-((1 - y) / 0.06))
        burn = np.clip((burn + edge * 0.8) * grill, 0, 0.92)
        img = img * (1 - burn[..., None]) + np.array([45, 20, 8], np.float32) * burn[..., None]
        img *= 0.93
    if char_top > 0:  # 윗 가장자리를 따라 까맣게 탄 줄
        line = 0.03 + 0.012 * stretched_noise(rng, 1, w, 30, 1)[0]
        c = np.clip(1 - np.abs(y - line) / 0.022, 0, 1) * char_top
        img = img * (1 - c[..., None]) + np.array([30, 15, 10], np.float32) * c[..., None]
    img = np.clip(img, 0, 255)
    # 위아래 가장자리가 살짝 물결치는 투명 테두리, 양 끝은 둥글게
    edge_t = 0.015 + 0.01 * (stretched_noise(rng, 1, w, 30, 1)[0] + 0.5)
    edge_b = 0.985 - 0.01 * (stretched_noise(rng, 1, w, 30, 1)[0] + 0.5)
    a = np.clip((y - edge_t) * h / 1.5, 0, 1) * np.clip((edge_b - y) * h / 1.5, 0, 1)
    x = np.arange(w)[None, :]
    a *= np.clip(np.minimum(x, w - 1 - x) / 3, 0, 1)
    rgba = np.dstack([img, a * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


make_strip(2200, 220, 1).save("strip.png")
make_strip(2200, 220, 2, grill=1.0).save("strip-grilled.png")
make_strip(1600, 900, 3, grill=0.25, char_top=1.0).convert("RGB").save("closeup.jpg", quality=92)
print("strip.png strip-grilled.png closeup.jpg")
