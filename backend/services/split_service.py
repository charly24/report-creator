import json
import os

from services.text_splitter import pares_segments

from vertexai.generative_models import GenerationConfig, GenerativeModel

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
                        "enum": [
                            "導入",
                            "職業機能の定義",
                            "want toの特定",
                            "Goal設定",
                            "自分ごと化",
                            "まとめ",
                        ],
                    },
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


SYSTEM_PROMPT = """
あなたは有能なAI秘書です。コーチングセッションの文字起こしデータを、以下の制約条件に忠実に従ってtopic分割しcharacterを抽出し、JSON形式で出力してください。

**想定出力**

```json
{
  "characters": {
    "client": "長岡さん", 
    "coach": "佐藤 武, 佐藤さん", 
    "introducer": "田中さん"
  },
  "topics": [
    {"start": "佐藤 武 00:06", "timestamp": "00:06", "topic": "導入"},
    {"start": "佐藤 武 05:12", "timestamp": "05:12", "topic": "職業機能の定義"},
    {"start": "長岡 諒 56:02", "timestamp": "56:02", "topic": "want toの特定"},
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

* 重要: startは、必ず入力文で利用されている文字を利用し、1文の改行までで区切って抽出してください。その値を利用して後続プロセスで分割するので、存在しない文字列だったり改行が含まれているとエラーになるためとても重要な制約です。
* 各topicは、以下のキーワードを参考に「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」「まとめ」のいずれかに分類されます。
  0. 導入：最初の頭出しで本日の流れや簡単に現状の外のGoalに関して説明して場所をセッティングする
  1. 職業機能の定義：クライアントがしている仕事を定義
  2. want toの特定：クライアントがやりたいこと/want toを人生を振り返って特定（want toの特定）
  3. Goal設定：そんなクライアントが未来においてやっていきたいことを定義
  4. 自分ごと化：Goalの中で具体的に何をするかの明確化
  5. まとめ：質疑応答やセッション全体のまとめなど
* topicは上記6つの中のいずれかをキーワードを利用して、どうしてもマッチしない場合は10文字以内の端的なtopic名にしてください。
* topicの変わり目で分割してください。topicと、startにはtopicが始まる行の先頭15文字の改行まで、文章にタイムスタンプがある場合そのタイムスタンプを出力してください。
* **出力:**
  * start: topicの先頭15文字、改行まで
  * timestamp: topic内の最初のタイムスタンプ
  * topic: 分類されたtopic(最大20文字、キーワードを参考にする)
* 文章の先頭に文字起こしサービスのメタ情報がある場合がありますが、それはスキップしてください。
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


async def analyze_text(text: str, prev: str = "", error: str = "", cnt: int = 0):
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

        for topic in res["topics"]:
            if text.find(topic["start"]) == -1:
                raise ValueError(f"Start not found in the text: {topic['start']}")
        if "characters" not in res:
            raise ValueError("No characters found")
        for key in ["client", "coach", "introducer"]:
            if key not in res["characters"] or not res["characters"][key]:
                res["characters"][key] = ""

        topics = await pares_segments(text, res["topics"])

        return res["characters"], topics
    except Exception as e:
        if cnt < 3 and "429" not in str(e):
            print(
                f"Split時にエラーが発生したので再実行します({cnt + 1}回目): {str(e)} "
            )
            return await analyze_text(text, current, str(e), cnt + 1)
        raise ValueError(f"Error splitting text: {str(e)}")
