import hashlib
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ.get("FPT_API_KEY", "").strip()

if not KEY:
    raise SystemExit("Thiếu Secret FPT_API_KEY.")

OUT = ROOT / "audio"
OUT.mkdir(exist_ok=True)
MP = OUT / "manifest.json"

questions = json.loads(
    (ROOT / "questions.json").read_text(encoding="utf-8")
)

manifest = {
    "voice": "leminh",
    "locale": "vi-VN",
    "region": "north",
    "complete": False,
    "files": {}
}

if MP.exists():
    manifest["files"] = json.loads(
        MP.read_text(encoding="utf-8")
    ).get("files", {})


def save_manifest():
    MP.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def request_tts(text):
    req = urllib.request.Request(
        "https://api.fpt.ai/hmi/tts/v5",
        data=text.encode("utf-8"),
        headers={
            "api_key": KEY,
            "voice": "leminh",
            "speed": "0",
            "format": "mp3"
        },
        method="POST"
    )

    time.sleep(10)

    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.load(r)

            if result.get("error") != 0:
                raise RuntimeError(
                    "FPT từ chối tạo giọng. "
                    "Kiểm tra dịch vụ và hạn mức tài khoản."
                )

            return result["async"]

        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise RuntimeError(
                    f"FPT trả HTTP {error.code}. "
                    "Kiểm tra tài khoản và hạn mức."
                ) from None

            if attempt == 6:
                raise RuntimeError(
                    "FPT vẫn giới hạn 429 sau nhiều lần chờ. "
                    "Kiểm tra hạn mức trước khi chạy tiếp."
                ) from None

            retry = (
                error.headers.get("Retry-After", "")
                if error.headers else ""
            )
            delay = max(
                15 * (2 ** attempt),
                int(retry) if retry.isdigit() else 0
            )

            print(
                f"FPT giới hạn tần suất: chờ {delay} giây.",
                flush=True
            )
            time.sleep(delay)


def download_audio(url, target):
    parsed = urlparse(url)
    host = parsed.hostname or ""

    if parsed.scheme != "https" or not (
        host.endswith(".amazonaws.com")
        or host.endswith(".fpt.ai")
    ):
        raise RuntimeError("Địa chỉ âm thanh không hợp lệ.")

    for attempt in range(30):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                audio = r.read()

            if len(audio) < 256:
                raise ValueError("Âm thanh chưa sẵn sàng.")

            target.write_bytes(audio)
            return

        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError
        ):
            time.sleep(min(2 + attempt, 15))

    raise RuntimeError("Không tải được âm thanh sau nhiều lần chờ.")


save_manifest()

for q in questions:
    if q["ans"]:
        answer = f'{q["ans"]}. {q["opts"][q["ans"]]}'
        hook = q["hook"] or (
            f'Gợi ý ôn tập tự động: {q["opts"][q["ans"]]}. '
            f'Đối chiếu: {q["basis"]}'
        )
    else:
        answer = (
            f'Chưa chốt đáp án. {q["answer_text"]}. '
            f'{q["note"]}'
        )
        hook = (
            "Câu chưa chốt: ghi nhớ điểm cần xác minh, "
            "không học thuộc một phương án."
        )

    parts = [
        ("q", "Câu hỏi. " + q["q"]),
        ("a", "Đáp án. " + answer + ". Móc nhớ. " + hook)
    ]

    for part, text in parts:
        name = f'{q["id"]}_{part}.mp3'
        target = OUT / name
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

        if (
            manifest["files"].get(name) == digest
            and target.exists()
        ):
            continue

        url = request_tts(text)
        download_audio(url, target)

        manifest["files"][name] = digest
        save_manifest()
        print("Đã tạo: " + name, flush=True)

manifest["complete"] = True
save_manifest()
print("Hoàn tất 780 bản ghi giọng nam miền Bắc.", flush=True)
