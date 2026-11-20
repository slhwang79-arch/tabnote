# 탭노트 (TabNote)

기타 TAB 악보를 적고, 기타 소리로 재생하고, 연주 녹음에서 음을 찾아 주는 웹앱입니다.
휴대폰·PC 브라우저에서 열어 "홈 화면에 추가"하면 설치형 앱(PWA)으로 쓸 수 있고, 한 번 연 뒤에는 인터넷 없이도 작동합니다.

## 파일 구성

| 파일 | 내용 |
|---|---|
| `index.html` | 화면, 악보 편집, 재생 엔진, 녹음 분석, MP3 저장 (CSS·JS 포함) |
| `guitar-samples.js` | 기타 녹음 샘플 (스틸·나일론 각 19음, MP3를 base64로 내장) → `window.GTR_SAMPLES` |
| `songs.js` | 예제 곡 데이터 (자작곡, 연습곡 1~3, 알함브라) → `window.ETUDES`, `window.ALH` |
| `lame.min.js` | MP3 인코더 (lamejs 1.2.1, LGPL-3.0, 원본 그대로) |
| `sw.js` | 오프라인 캐시 (서비스 워커). 파일을 바꾸면 `CACHE` 버전 숫자를 올릴 것 |
| `manifest.webmanifest`, `icon-*.png` | 앱 설치 정보와 아이콘 |
| `netlify.toml` | Netlify 배포 설정 (공개할 파일 목록, 캐시 설정) |
| `build-artifact.py` | Claude 아티팩트용 사본 만들기 (아래 참고) |

빌드 과정은 없습니다. 아무 정적 웹 서버로 폴더를 열면 됩니다.

```bash
python3 -m http.server 8000   # http://localhost:8000
```

## 악보 데이터 구조

- `st.cols[칸][줄]` — 줄 번호 0 = 1번줄(높은 e) … 5 = 6번줄(낮은 E). 값은 프렛 번호(숫자), `'x'`(뮤트음, 화면 표기 `M.`), 또는 `null`(빈 칸, 앞 음이 계속 울림)
- `st.res` — 보통 박 하나를 몇 칸으로 나눌지 (2 = 8분음표, 4 = 16분음표, 8 = 32분음표). 이 값을 바꾸면 음이 같은 박자 위치로 옮겨짐
- `st.trip` — 셋잇단 박 번호 목록 (곡 처음부터 0, 1, 2…). 셋잇단 박은 `res×1.5`칸 (8분 셋잇단 3칸, 16분 셋잇단 6칸, 32분 셋잇단 12칸). 그래서 `st.cols`는 박마다 칸 수가 다를 수 있고, 칸 위치·시간은 `relayout()`이 계산한 `L`(박 시작 칸 `bs`, 마디 시작 칸 `ms`, 칸의 박 위치 `ct`)로 구함. 예전 `res: 6` 저장본은 불러올 때 `res: 4` + 모든 박 셋잇단으로 바뀜
- `st.beats` — 한 마디의 박 수 (2/4, 3/4, 4/4)
- `st.pm` — 팜뮤트가 걸린 칸 번호 목록
- `st.bpm`, `st.capo`, `st.title`, `st.note`
- 저장은 브라우저 localStorage (`tabnote.current`, `tabnote.songs`, `tabnote.opts`)
- `songs.js`의 곡 데이터 형식: `"<칸><줄 a~f><프렛 또는 x>"`를 공백으로 이은 문자열. 줄 a = 1번줄 … f = 6번줄

## 지금까지의 주요 결정

- **음색**: 기본은 실제 기타 녹음 샘플(FluidR3 GM). 3반음 간격 샘플을 playbackRate로 높낮이 조절. 이전 합성음(Karplus-Strong)도 "합성음" 옵션으로 남겨 둠
- **스트로크**: 한 칸에 3음 이상이면 줄을 차례로 울림. 박 위·낮은 줄 포함 = 다운(낮은 줄부터 11ms 간격), 박 사이·높은 4줄만 = 업(높은 줄부터 8ms)
- **녹음 음 인식**: 스펙트럼 변화로 음 시작점을 찾고, 직전 소리를 빼고 새로 생긴 소리에서 최대 3음을 찾음. 통기타 몸통 울림(약 85~106Hz)은 배음이 약하면 음으로 치지 않음. 0.5초 이내 베이스+멜로디는 한 칸으로 묶음(옵션)
- **줄·프렛 배정**: 소리만으로는 어느 줄에서 쳤는지 알 수 없으므로 "손 위치" 옵션과 카드 눌러 바꾸기(⇄)로 보완
- **MP3 저장**: OfflineAudioContext로 곡 전체를 렌더링 후 lamejs로 인코딩. 실패하면 WAV

## 배포

Netlify에서 이 저장소를 연결하면 main이 바뀔 때마다 자동 배포됩니다.
(Netlify → Add new site → Import an existing project → GitHub → 이 저장소 선택. 빌드 설정은 `netlify.toml`이 정하므로 화면에서는 비워 두면 됨)

`netlify.toml`은 앱에 필요한 파일만 `public/`으로 모아 그 폴더만 공개합니다. 앱 파일을 새로 추가하면 `netlify.toml`의 복사 목록과 `sw.js`의 `CORE` 목록에 함께 넣어야 합니다.

## Claude 아티팩트로 올리기

Claude 안에서 쓰는 사본(https://claude.ai/artifact/GgRGKDE66ejFTjJd8ER1Ra)은 아래 명령으로 만듭니다.

```bash
python3 build-artifact.py   # 결과: dist/artifact/ (git에는 올리지 않음)
```

`dist/artifact/tabnote.html`을 페이지로, `guitar-samples.js`·`songs.js`·`lame.min.js`를 함께 올리는 파일로 게시합니다. 아티팩트 사본은 앱 설치 버튼·아이폰 설치 안내·서비스 워커를 빼고, 마이크를 바로 쓸 수 없을 때 녹음 앱이나 파일 고르기를 안내합니다. `index.html`이 바뀌어 바꿀 부분을 찾지 못하면 스크립트가 멈추고 어느 부분인지 알려 줍니다.

## 라이선스와 출처

- 기타 샘플: FluidR3 GM 사운드폰트 (Frank Wen), CC BY 3.0 — gleitz/midi-js-soundfonts 변환본을 잘라 다시 인코딩
- 알함브라 궁전의 추억 음 데이터: The Mutopia Project 악보 (조판 Stewart Holmes), CC BY-SA 3.0
- MP3 인코더: lamejs, LGPL-3.0
- 자작곡: 사용자 가족의 창작곡. 연습곡 1~3: 이 앱을 위해 새로 만든 곡
- 저작권이 있는 곡(대중가요 등)의 악보는 예제 곡으로 넣지 않음
