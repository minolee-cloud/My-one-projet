# My-one-projet
## laugh-loop: 웃음 무한루프 영상

강아지가 점점 크게 웃다가 고양이로 변하고, 고양이도 웃다가 다시 강아지로 돌아오는 16초 무한루프 영상입니다.

- `laugh-loop/laugh-loop.mp4`: 완성 영상 (720x1280 세로, 쇼츠/릴스용, 소리 포함)
- `laugh-loop/index.html`: 브라우저에서 여는 애니메이션 (버튼을 누르면 소리와 함께 재생)
- 다시 만들기: `cd laugh-loop && python3 make_audio.py && node render.js` (numpy, playwright, ffmpeg 필요)

## rose-jjondeugi: 장미와 쫀드기 (호러코믹)

평화로운 장미가 꿈틀대다 쫀드기로 변하고, 다시 자라난 장미가 그 쫀드기를 먹어치우는 24초 호러코믹 영상입니다. 직접 찍은 장미 사진에서 꽃봉오리를 오려내 움직였습니다.

- `rose-jjondeugi/rose-jjondeugi.mp4`: 완성 영상 (720x1280 세로, 소리 포함)
- `rose-jjondeugi/index.html`: 브라우저에서 여는 애니메이션
- 다시 만들기: `cd rose-jjondeugi && python3 prepare.py && python3 make_audio.py && node render.js` (numpy, pillow, playwright, ffmpeg 필요)

## rose-jjondeugi-match: 장미, 그리고 쫀드기 (닮은꼴)

장미와 쫀드기가 색과 모양이 닮았다는 데 초점을 맞춘 30초 영상입니다. 1막은 우아한 슬로우모션(하프·현악 왈츠), 2막은 같은 멜로디를 귀엽게(실로폰·우쿨렐레) 편곡했습니다.

- `rose-jjondeugi-match/rose-jjondeugi-match.mp4`: 완성 영상 (720x1280 세로, 소리 포함)
- `rose-jjondeugi-match/index.html`: 브라우저에서 여는 애니메이션
- 쫀드기는 사진 대신 `make_jjondeugi.py` 로 직접 그렸습니다 (줄무늬, 결, 설탕 알갱이, 구운 자국)
- 글꼴: 고운바탕, 나눔명조, 주아 (SIL Open Font License, Google Fonts)
- 다시 만들기: `cd rose-jjondeugi-match && python3 make_jjondeugi.py && python3 make_audio.py && node render.js` (numpy, pillow, playwright, ffmpeg 필요)
