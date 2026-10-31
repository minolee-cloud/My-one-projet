"""사진에서 장미 꽃봉오리를 오려내고(bud.png), 꽃봉오리가 없는 배경(plate.jpg)을 만든다."""
import numpy as np
from PIL import Image, ImageFilter

img = Image.open("src/rose-wide.jpg").convert("RGB").resize((2000, 1126), Image.LANCZOS)
rgb = np.asarray(img).astype(np.float32)
hsv = np.asarray(img.convert("HSV")).astype(np.float32)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

# 꽃잎: 채도 높은 빨강~노랑, 봉오리 주변 영역만
warm = (h < 48) | (h > 225)
mask = warm & (s > 60) & (v > 110)
box = np.zeros_like(mask)
box[200:860, 700:1320] = True
mask &= box


def grow(m, r):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(r))) > 127


def shrink(m, r):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(r))) > 127


mask = shrink(grow(mask, 15), 15)  # 구멍 메우기
mask = grow(shrink(mask, 5), 5)    # 잡티 제거
# 바깥에서 닿지 않는 구멍만 채운다
from PIL import ImageDraw
fl = Image.fromarray((mask * 255).astype(np.uint8)).copy()
ImageDraw.floodfill(fl, (0, 0), 128)
mask = np.asarray(fl) != 128

ys, xs = np.nonzero(mask)
x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
print("bud box", x0, y0, x1, y1)

alpha = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
bud = img.copy()
bud.putalpha(alpha)
bud.crop((x0, y0, x1, y1)).save("bud.png")

# 꽃봉오리 자리를 주변 색으로 채운다: 알려진 픽셀만 흐리게 평균(정규화 컨볼루션). 배경이 흐려서 티가 덜 남
hole = grow(mask, 25)
known = (~hole).astype(np.float32)


def blur(arr, r):
    return np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)


# 1/4 크기에서 큰 반경부터 작은 반경 순으로 채운 뒤 원래 크기로 키운다
H, W = mask.shape
sm = (W // 4, H // 4)
rgb_s = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize(sm, Image.BILINEAR)).astype(np.float32)
known_s = np.asarray(Image.fromarray((known * 255).astype(np.uint8)).resize(sm, Image.BILINEAR)).astype(np.float32) / 255
known_s = (known_s > 0.99).astype(np.float32)


def pyr_fill(img, k):
    """구멍(k=0)을 피라미드로 줄여가며 주변 평균색으로 채운다."""
    h, w = k.shape
    if k.min() > 0 or min(h, w) < 2:
        return img
    h2, w2 = (h + 1) // 2 * 2, (w + 1) // 2 * 2
    ip, kp = np.zeros((h2, w2, 3)), np.zeros((h2, w2))
    ip[:h, :w], kp[:h, :w] = img * k[..., None], k
    ks = kp.reshape(h2 // 2, 2, w2 // 2, 2).sum((1, 3))
    small = ip.reshape(h2 // 2, 2, w2 // 2, 2, 3).sum((1, 3)) / np.maximum(ks, 1e-6)[..., None]
    small = pyr_fill(small, (ks > 0).astype(np.float32))
    up = np.asarray(Image.fromarray(np.clip(small, 0, 255).astype(np.uint8)).resize((w2, h2), Image.BILINEAR)).astype(np.float32)[:h, :w]
    return np.where(k[..., None] > 0, img, up)


fill_s = blur(pyr_fill(rgb_s, known_s), 3)
fill_s = np.where(known_s[..., None] > 0, rgb_s, fill_s)
fill = np.asarray(Image.fromarray(np.clip(fill_s, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32)
noise = np.random.default_rng(1).normal(0, 4, fill.shape)
soft = blur(hole * 255, 6)[..., None] / 255
plate = rgb * (1 - soft) + (fill + noise) * soft
Image.fromarray(np.clip(plate, 0, 255).astype(np.uint8)).save("plate.jpg", quality=92)
Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
bud = img.copy()
bud.putalpha(alpha)
bud.crop((x0, y0, x1, y1)).save("bud.png")

# 꽃봉오리 자리를 주변 색으로 번지게 채운다 (배경이 흐려서 티가 덜 남)
Image.fromarray((mask * 255).astype(np.uint8)).save("/tmp/claude-0/-home-user-My-one-projet/e38bacf0-0110-5715-bdf9-8335e4452ca7/scratchpad/mask.png")
