import json
import os

from vertexai.generative_models import GenerationConfig, GenerativeModel

# import typing_extensions as typing
# class Segment(typing.TypedDict):
#     start: str
#     timestamp: str
#     topic: str
#     token: str


response_schema = {
    "type": "OBJECT",
    "properties": {
        "topics": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "start": {"type": "STRING"},
                    "timestamp": {"type": "STRING"},
                    "topic": {
                        "type": "STRING",
                        "description": "「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」「まとめ」から選択",
                    },
                    "token": {"type": "INTEGER"},
                    "confidence": {"type": "INTEGER"},
                },
            },
        },
        "characters": {
            "type": "OBJECT",
            "properties": {
                "client": {"type": "STRING"},
                "coach": {"type": "STRING"},
                "introducer": {"type": "STRING"},
            },
        },
    },
}

format_model = GenerativeModel(model_name=os.getenv("GEMINI_MODEL_PRO"))

FORMAT_PROMPT = """
あなたは有能なAI秘書です。コーチングセッションの文字起こしデータを、以下の制約条件に従ってtopic分割しcharacterを抽出し、JSON形式で出力してください。

**想定出力**

```json
{
  "characters": {
    "client": "山田さん", 
    "coach": "佐藤 武, 佐藤さん", 
    "introducer": "田中さん"
  },
  "topics": [
    {“start”: "長岡 諒 00:06", "timestamp": “00:00”, “topic”: “導入”, "token": 3512},
    {“start”: "長岡 諒 05:12", "timestamp": “05:12”, “topic”: “職業機能の定義”, "token": 5880},
    {“start”: "長岡 諒 45:03", "timestamp": “45:03”, “topic”: “職業機能の定義 (2)”, "token": 2540},
    {“start”: "長岡 諒 56:02", "timestamp": “56:02”, “topic”: “want toの特定”, "token": 4183},
    ...
  ]
}
```

**制約条件(characters)**

以下の3つの登場人物を抽出してください。
* client: コーチングセッションのクライアント
* coach: コーチ、場をリードしてクライアントに質問して導く
* introducer: コーチにクライアントを紹介した人

**制約条件(topics)**

* **トークン長:** 分割後の各セグメントのトークン長は、最大6000トークンを目安としてください。
* 各セグメントは、以下のキーワードを参考に「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」「まとめ」のいずれかに分類されます。
  0. 導入：最初の頭出しで本日の流れや簡単に現状の外のGoalに関して説明して場所をセッティングする
  1. 職業機能の定義：クライアントがしている仕事を定義
  2. want toの特定：クライアントがやりたいこと/want toを人生を振り返って特定（want toの特定）
  3. Goal設定：そんなクライアントが未来においてやっていきたいことを定義
  4. 自分ごと化：Goalの中で具体的に何をするかの明確化
  5. まとめ：質疑応答やセッション全体のまとめなど
* 重要: topicは最大20文字までで、上記6つの中のいずれかをキーワードを利用してください。
* ある程度のtopic別に区切ってください。topicと、startにはtopicが始まる行の先頭15文字、文章にタイムスタンプはある場合とない場合がありますがある場合はそのタイムスタンプ、topic内に含まれるtoken数を出力してください。
* 重要: startは、入力文と同じ文字を使ってください。その値を利用して後続プロセスで分割するので、存在しない文字列だとエラーになるため重要です。
* 60分のセッションだと4~5個くらいに分割される想定で、小さく分割しすぎず、できるだけ1topic毎に最大トークン数に近くなるよう分割してください。
* 1つのtopicで30分以上かかっている場合、最大トークン長を超えることが多いので分割して、その際topic名を"導入 (2)"のように変更してください。
* 重要: 分割しすぎないようにして、最大でも8分割以内に抑えてください。基本的に5分割でOKですし、300分を超える文字起こしは想定していません。
* **分割基準:** 文構造、時間経過、キーワード頻度などを複合的に判断し、文脈の切れ目で分割します。
* **出力:**
  * start: セグメントの先頭15文字
  * timestamp: セグメント内の最初のタイムスタンプ
  * topic: 分類されたtopic(最大20文字、キーワードを参考にする)
  * token: セグメント内のトークン数
  * confidence: 分割結果の信頼度
* 1トピックに含まれるtoken数が最大トークン長を超える場合は文脈の切れ目で適切に分割してください。しかし、分割数は最小限にしてください
* 文章の先頭に文字起こしサービスのメタ情報がある場合がありますが、それはスキップしてください。

**入力文**
"""


async def analyze_text(text: str, cnt: int = 0) -> list:
    try:
        raw_response = format_model.generate_content(
            FORMAT_PROMPT + str(text),
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                max_output_tokens=3000,
            ),
        )
        res = json.loads(raw_response.text)
        for topic in res["topics"]:
            if text.find(topic["start"]) == -1:
                raise ValueError(f"Start not found in the text: {topic['start']}")
        if "characters" not in res:
            raise ValueError("No characters found")
        if "client" not in res["characters"]:
            res["characters"]["client"] = ""
        if "coach" not in res["characters"]:
            res["characters"]["coach"] = ""
        if "introducer" not in res["characters"]:
            res["characters"]["introducer"] = ""
        return res
    except Exception as e:
        if cnt < 3 and "429" not in str(e):
            print(
                f"Split時にエラーが発生したので再実行します({cnt + 1}回目): {str(e)} "
            )
            return await analyze_text(
                f"{text}\n\n**前回実行時エラー内容**\n{str(e)}", cnt + 1
            )
        raise ValueError(f"Error splitting text: {str(e)}")
