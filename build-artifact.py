#!/usr/bin/env python3
"""탭노트를 Claude 아티팩트로 올릴 사본을 만듭니다.

    python3 build-artifact.py        # 결과: dist/artifact/

만드는 것
- dist/artifact/tabnote.html  : index.html에서 <title>부터의 head 내용과 body만 뽑은 페이지
  (아티팩트가 문서 뼈대를 직접 씌우므로 doctype·charset·manifest·아이콘 링크는 뺌)
- guitar-samples.js, songs.js, lame.min.js : 그대로 복사 (페이지 옆에 함께 올리는 파일)

아티팩트용으로 바꾸는 것
- "앱 설치" 버튼, 아이폰 홈 화면 추가 안내, 서비스 워커·설치 코드 제거 (아티팩트에서는 쓸 수 없음)
- 마이크 오류 문구: 아티팩트에서는 마이크를 바로 쓸 수 없으므로 녹음 앱·파일 고르기를 안내

index.html이 바뀌어 아래 바꿀 문장을 찾지 못하면 멈추고 어느 부분인지 알려 줍니다.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "artifact"
FILES = ["guitar-samples.js", "songs.js", "lame.min.js"]


def fail(msg):
    sys.exit(f"빌드 실패: {msg}")


def cut(text, start, end, what):
    """start 표시부터 end 표시 직전까지를 지움."""
    i, j = text.find(start), text.find(end)
    if i < 0 or j < 0 or j < i:
        fail(f"{what} 부분을 찾지 못했습니다. index.html을 확인하세요.")
    return text[:i] + text[j:]


def swap(text, old, new, what):
    n = text.count(old)
    if n != 1:
        fail(f"{what} 문장이 {n}번 나옵니다 (1번이어야 함). index.html을 확인하세요.")
    return text.replace(old, new)


def main():
    src = (ROOT / "index.html").read_text(encoding="utf-8")

    for mark in ("<title>", "</head>", "<body>", "</body>"):
        if mark not in src:
            fail(f"index.html에 {mark}가 없습니다.")
    head = src[src.index("<title>"):src.index("</head>")]
    body = src[src.index("<body>") + len("<body>"):src.rindex("</body>")]

    body = swap(body, '<button class="btn primary" id="installBtn" hidden>📲 앱 설치</button>', "",
                "앱 설치 버튼")
    body = cut(body, '<p class="hint" id="iosHint"', '<input class="title-in"', "아이폰 설치 안내")
    body = cut(body, "/* ---------- 앱 설치 (PWA) ---------- */", "/* ---------- 연주 저장",
               "앱 설치 코드")
    body = swap(
        body,
        "recMsg('마이크를 쓸 수 없습니다. 브라우저에서 마이크 권한을 허용했는지 확인하세요. "
        "카카오톡 안에서 열었다면 오른쪽 위 메뉴의 \"다른 브라우저로 열기\"로 크롬이나 사파리에서 열어 주세요.')",
        "recMsg('이 화면에서는 마이크를 바로 쓸 수 없습니다. "
        "\"● 녹음 앱으로 녹음\"이나 \"녹음 파일 고르기\"로 녹음 파일을 넣어 주세요.')",
        "마이크 오류 문구",
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "tabnote.html").write_text(head + "\n" + body, encoding="utf-8")
    for f in FILES:
        shutil.copy(ROOT / f, OUT / f)

    print(f"완료: {OUT.relative_to(ROOT)}/")
    for f in ["tabnote.html"] + FILES:
        print(f"  {f:20s} {(OUT / f).stat().st_size:>9,d} bytes")


if __name__ == "__main__":
    main()
