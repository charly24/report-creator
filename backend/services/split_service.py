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
                            "職業機能の定義 (2)",
                            "職業機能の定義 (3)",
                            "want toの特定",
                            "want toの特定 (2)",
                            "want toの特定 (3)",
                            "Goal設定",
                            "Goal設定 (2)",
                            "Goal設定 (3)",
                            "自分ごと化",
                            "自分ごと化 (2)",
                            "自分ごと化 (3)",
                            "まとめ",
                            "まとめ (2)",
                            "まとめ (3)",
                        ],
                    },
                    "token": {"type": "INTEGER", "description": "topic内のトークン数"},
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
    {“start”: "佐藤 武 00:06", "timestamp": “00:06”, “topic”: “導入”, "token": 3512},
    {“start”: "佐藤 武 05:12", "timestamp": “05:12”, “topic”: “職業機能の定義”, "token": 5880},
    {“start”: "佐藤 武 35:03", "timestamp": “35:03”, “topic”: “職業機能の定義 (2)”, "token": 2540},
    {“start”: "長岡 諒 56:02", "timestamp": “56:02”, “topic”: “want toの特定”, "token": 5183},
    {“start”: "佐藤 武 1:23:07", "timestamp": “1:23:07”, “topic”: “want toの特定 (2)”, "token": 4183},
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

* 分割後の各topicのトークン長は、最大6000トークンを目安としてください。
* 各topicは、以下のキーワードを参考に「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」「まとめ」のいずれかに分類されます。
  0. 導入：最初の頭出しで本日の流れや簡単に現状の外のGoalに関して説明して場所をセッティングする
  1. 職業機能の定義：クライアントがしている仕事を定義
  2. want toの特定：クライアントがやりたいこと/want toを人生を振り返って特定（want toの特定）
  3. Goal設定：そんなクライアントが未来においてやっていきたいことを定義
  4. 自分ごと化：Goalの中で具体的に何をするかの明確化
  5. まとめ：質疑応答やセッション全体のまとめなど
* topicは上記6つの中のいずれかをキーワードを利用して、どうしてもマッチしない場合は10文字以内の端的なtopic名にしてください。
* ある程度のtopic別に区切ってください。topicと、startにはtopicが始まる行の先頭15文字、文章にタイムスタンプはある場合とない場合がありますがある場合はそのタイムスタンプ、topic内に含まれるtoken数を出力してください。
* 重要: startは、必ず入力文で利用されている文字を使ってください。その値を利用して後続プロセスで分割するので、存在しない文字列だとエラーになるため重要です。
* 60分のセッションだと最大4~5個くらいに分割される想定で、小さく分割しすぎず、できるだけ1topic毎に最大トークン数に近くなるよう分割してください。
* 重要: 1つのtopicで30分以上かかっている場合、整形する際に最大トークン長を超えることが多いので30分前後の区切りの良い箇所で分割して、その際topic名を"導入 (2)"のように変更してください。
* **分割基準:** 文構造、時間経過、キーワード頻度などを複合的に判断し、文脈の切れ目で分割します。
* **出力:**
  * start: topicの先頭15文字
  * timestamp: topic内の最初のタイムスタンプ
  * topic: 分類されたtopic(最大20文字、キーワードを参考にする)
  * token: topic内のトークン数
  * confidence: 分割結果の信頼度
* 1トピックに含まれるtoken数が最大トークン長を超える場合は文脈の切れ目で適切に分割してください。しかし、分割数は最小限にしてください
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

from datetime import datetime


def parse_time(time_str):
    """時間フォーマットを動的に認識し、datetimeオブジェクトを返す"""
    try:
        if len(time_str) == 5:  # mm:ss
            time_format = "%M:%S"
        elif len(time_str) == 7 or len(time_str) == 8:  # hh:mm:ss
            time_format = "%H:%M:%S"
        return datetime.strptime(time_str, time_format)
    except ValueError as e:
        print(f"Error parsing time: {e}")
        return None


def time_difference(start, end):
    """開始時間と終了時間の差を分単位で計算する"""
    start_time = parse_time(start)
    end_time = parse_time(end)
    return (end_time - start_time).total_seconds() / 60


def compress_topics(data):
    """指定されたルールに従ってトピックリストを圧縮する"""
    # (2)や(3)を無視
    filtered_data = [
        item
        for item in data
        if not any(suffix in item["topic"] for suffix in [" (2)", " (3)"])
    ]

    # 次のtopicまでの時間を計算
    for i in range(len(filtered_data) - 1):
        filtered_data[i]["duration"] = time_difference(
            filtered_data[i]["timestamp"], filtered_data[i + 1]["timestamp"]
        )

    # 最後のtopicの次の時間を100分と仮定
    filtered_data[-1]["duration"] = 100

    # 連続する同じtopicを削除
    def remove_redundant_topics(data):
        i = 0
        while i < len(data) - 1:
            if (
                data[i]["topic"] == data[i + 1]["topic"]
                and data[i + 1]["duration"] < 30
            ):
                data.pop(i + 1)
            else:
                i += 1
        return data

    # 削除が発生しなくなるまで繰り返し
    previous_length = -1
    while previous_length != len(filtered_data):
        previous_length = len(filtered_data)
        filtered_data = remove_redundant_topics(filtered_data)

    return filtered_data


async def analyze_text(text: str, prev: str = "", error: str = "", cnt: int = 0):
    try:
        prompt = text
        if error:
            print(error, prev)
            prompt = f"""
# 前回のエラー内容
{error}

# 前回の出力（この結果を60点として、30分以上のtopicがあれば分割したりjsonのformatを見直してください）
{prev}

# 入力文
{prompt}
"""
        raw_response = model.generate_content(prompt)
        res = json.loads(raw_response.text)
        compress = compress_topics(res["topics"])
        if len(compress) != len(res["topics"]):
            # どうしてもtopic分割のコントロールが難しいため、分割自体はある程度自由にさせてその後圧縮するアプローチに修正
            # 分割は、Geminiが16kまでであるためどうしても必要、実際30分程度までなら1topicで16k以内で収まる
            res["topics"] = compress
        for topic in res["topics"]:
            if text.find(topic["start"]) == -1:
                raise ValueError(f"Start not found in the text: {topic['start']}")
        if "characters" not in res:
            raise ValueError("No characters found")
        for key in ["client", "coach", "introducer"]:
            if key not in res["characters"] or not res["characters"][key]:
                res["characters"][key] = ""

        segments = await pares_segments(text, res["topics"])

        for segment in segments:
            # 6000トークン以上のセグメントがある場合はエラーという命令ですが、実際は16k程度まで許容されます
            if segment["token"] > 16000:
                raise ValueError(
                    f"Topic too long: {segment['topic']}, {segment['token']} tokens, please split it."
                )
        return res["characters"], segments
    except Exception as e:
        if cnt < 3 and "429" not in str(e):
            print(
                f"Split時にエラーが発生したので再実行します({cnt + 1}回目): {str(e)} "
            )
            return await analyze_text(
                text, raw_response.text if raw_response else "", str(e), cnt + 1
            )
        raise ValueError(f"Error splitting text: {str(e)}")
