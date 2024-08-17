import json
import os

from services.text_splitter import pares_segments

from vertexai.generative_models import GenerationConfig, GenerativeModel

response_schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "start": {"type": "STRING"},
            "timestamp": {"type": "STRING"},
        },
    },
}


SYSTEM_PROMPT = """
あなたは有能なAI秘書です。コーチングセッションの文字起こしデータを、以下の制約条件に忠実に従って分割し、JSON形式で出力してください。

**想定出力**

```json
[
  {"start": "佐藤 武 00:06", "timestamp": "00:06"},
  {"start": "佐藤 武 23:12", "timestamp": "23:12"},
  {"start": "長岡 諒 45:22", "timestamp": "45:22"},
  ...
]
```

**制約条件**

* 重要: startは、必ず入力文で利用されている文字を利用し、1文の改行までで区切って抽出してください。その値を利用して後続プロセスで分割するので、存在しない文字列だったり改行が含まれているとエラーになるためとても重要な制約です。
* 分割基準は、文構造、時間経過、キーワード頻度などを複合的に判断し、約20~23分毎に分割してください。
* startには分割後の文章が始まる行の先頭15文字の改行まで、文章にタイムスタンプがある場合そのタイムスタンプを出力してください。
* 23分を超えない範囲で分割数は最小限にしてください。40分の文章の分割なら2つに、70分の文章の分割なら4つに分割するようにしてください。
* **出力:**
  * start: 分割された文章の先頭15文字
  * timestamp: 分割された文章の最初のタイムスタンプ
"""

model = GenerativeModel(
    model_name=os.getenv("GEMINI_MODEL_PRO"),
    system_instruction=[
        SYSTEM_PROMPT,
    ],
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        response_schema=response_schema,
        max_output_tokens=1000,
    ),
)


async def split_detail(text, prev: str = "", error: str = "", cnt: int = 0):
    current = ""
    try:
        prompt = text
        if error:
            print(error, prev)
            prompt = f"""
{cnt}回目の試行です。前回のエラー内容を確認して同じ間違いを繰り返さず次はエラーにならないよう出力してください。

# 前回のエラー内容
{error}

# 前回の出力
{prev}

# 入力文
{prompt}
"""
        raw_response = model.generate_content(prompt)
        current = raw_response.text
        res = json.loads(raw_response.text)

        for segment in res:
            if text.find(segment["start"]) == -1:
                raise ValueError(f"Start not found in the text: {segment['start']}")

        segments = await pares_segments(text, res)

        return segments
    except Exception as e:
        if cnt < 3 and "429" not in str(e):
            print(
                f"Detail Split時にエラーが発生したので再実行します({cnt + 1}回目): {str(e)} "
            )
            return await split_detail(text, current, str(e), cnt + 1)
        raise ValueError(f"Error splitting text: {str(e)}")
