import google.generativeai as genai
import typing_extensions as typing
import json
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class Segment(typing.TypedDict):
    start: str
    timestamp: str
    topic: str
    token: str

format_model = genai.GenerativeModel(
    model_name=os.getenv("GEMINI_MODEL_PRO"), 
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": list[Segment]
    }
)

FORMAT_PROMPT = """
あなたは有能なAI秘書です。コーチングセッションの文字起こしデータを、以下の制約条件に従って分割し、JSON形式で出力してください。

**制約条件**

* **トークン長:** 分割後の各セグメントのトークン長は、最大6000トークンを目安としてください。
* 各セグメントは、以下のキーワードを参考に「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」「まとめ」のいずれかに分類されます。
  0. 導入：最初の頭出しで本日の流れや簡単に現状の外のGoalに関して説明して場所をセッティングする
  1. 職業機能の定義：クライアントがしている仕事を定義
  2. want toの特定：クライアントがやりたいこと/want toを人生を振り返って特定（want toの特定）
  3. Goal設定：そんなクライアントが未来においてやっていきたいことを定義
  4. 自分ごと化：Goalの中で具体的に何をするかの明確化
  5. まとめ：質疑応答やセッション全体のまとめなど
* ある程度のtopic別に区切ってください。topicと、startにはtopicが始まる行の先頭15文字、文章にタイムスタンプはある場合とない場合がありますがある場合はそのタイムスタンプ、topic内に含まれるtoken数を出力してください。
* startは、入力文と同じ文字を使ってください。その値を利用して後続プロセスで分割するので、存在しない文字列だとエラーになるため重要です。
* 60分のセッションだと4~5個くらいに分割される想定で、小さく分割しすぎず、できるだけ1topic毎に最大トークン数に近くなるよう分割してください。
* 1つのtopicで30分以上かかっている場合、最大トークン長を超えることが多いので分割してください
* **分割基準:** 文構造、時間経過、キーワード頻度などを複合的に判断し、文脈の切れ目で分割します。
* **出力:**
  * start: セグメントの先頭15文字
  * timestamp: セグメント内の最初のタイムスタンプ
  * topic: 分類されたtopic(最大20文字、キーワードを参考にする)
  * token: セグメント内のトークン数
  * reason: 分割理由
  * confidence: 分割結果の信頼度
* 1トピックに含まれるtoken数が最大トークン長を超える場合は文脈の切れ目で適切に分割してください。しかし、分割数は最小限にしてください
* 文章の先頭に文字起こしサービスのメタ情報がある場合がありますが、それはスキップしてください

**想定出力**

```json
[
  {“start”: "長岡 諒 00:06", "timestamp": “00:00”, “topic”: “導入”, "token": 3512},
  {“start”: "長岡 諒 05:12", "timestamp": “05:12”, “topic”: “職業機能の定義”, "token": 5880},
  {“start”: "長岡 諒 45:03", "timestamp": “45:03”, “topic”: “職業機能の定義 (2)”, "token": 2540},
  {“start”: "長岡 諒 56:02", "timestamp": “56:02”, “topic”: “want toの特定”, "token": 4183},
  ...
]

"""

FORMAT_PROMPT = """あなたは有能な秘書です。自身のアウトプットが制約条件に従っているか忠実に守り、仕事をしています。
コーチングセッションの文字起こしデータを、指定された制約条件に厳密に従って分割してください。

# 制約条件
- 分割の最大トークン長は6000トークンです。それを超えないようにしてください。
- 文章を分割するために、どこで分割するのが適切かをjson形式で出力してください
- 想定アウトプットのように、ある程度のtopic別に区切ってほしく、topicと、startにはtopicが始まる行の先頭15文字、文章にタイムスタンプはある場合とない場合がありますがある場合はそのタイムスタンプ、topic内に含まれるtoken数を出力してください
- startは、入力文と同じ文字を使ってください。その値を利用して後続プロセスで分割するので、存在しない文字列だとエラーになるため重要です
- 60分のセッションだと4~5個くらいに分割される想定で、小さく分割しすぎず、できるだけ1topic毎に最大トークン数に近くなるよう分割してください。
- 1つのtopicで30分以上かかっている場合、最大トークン長を超えることが多いので分割してください
- topicは基本的に「導入」「職業機能の定義」「want toの特定」「Goal設定」「自分ごと化」という流れで順番に進みます。
1. 導入：最初の頭出しで本日の流れや簡単に現状の外のGoalに関して説明して場所をセッティングする
2. 職業機能の定義：クライアントがしている仕事を定義
3. want toの特定：クライアントがやりたいこと/want toを人生を振り返って特定（want toの特定）
4. Goal設定：そんなクライアントが未来においてやっていきたいことを定義
5. 自分ごと化：Goalの中で具体的に何をするかの明確化
- 1トピックに含まれるtoken数が最大トークン長を超える場合は文脈の切れ目で適切に分割してください。しかし、分割数は最小限にしてください
- 文章の先頭に文字起こしサービスのメタ情報がある場合がありますが、それはスキップしてください
- トピックは最大20文字以内で出力してください

# 想定アウトプット
[
  {“start”: "長岡 諒 00:06", "timestamp": “00:00”, “topic”: “導入”, "token": 3512},
  {“start”: "長岡 諒 05:12", "timestamp": “05:12”, “topic”: “職業機能の定義”, "token": 5880},
  {“start”: "長岡 諒 45:03", "timestamp": “45:03”, “topic”: “職業機能の定義 (2)”, "token": 2540},
  {“start”: "長岡 諒 56:02", "timestamp": “56:02”, “topic”: “want toの特定”, "token": 4183},
…
]

# 入力文
"""

async def split_text(text: str) -> list:
    # return [{'start': '長岡 諒 00:13', 'timestamp': '00:13', 'topic': '導入'}, {'start': '長岡 諒 03:32', 'timestamp': '03:32', 'topic': '職業機能の定義'}, {'start': '長岡 諒 18:46', 'timestamp': '18:46', 'topic': 'want toの特定'}, {'start': '長岡 諒 47:37', 'timestamp': '47:37', 'topic': 'Goal設定'}, {'start': '長岡 諒 56:57', 'timestamp': '56:57', 'topic': '自分ごと化'}]
    # return json.loads('[{"start": "ああ、だめです。ありがとうございます、本日は。", "timestamp": "00:10", "token": "3512", "topic": "導入"}, {"start": "はい。 今、 広 告 制 作 に、 もう 30 年 ぐ らい か。", "timestamp": "08:29", "token": "4180", "topic": "職業機能の定義"}, {"start": "そうですね。 な お か つ、 価 値 提 供 でき て る こと ですね。", "timestamp": "13:36", "token": "5820", "topic": "want toの特定"}, {"start": "そうだ な。", "timestamp": "44:23", "token": "3960", "topic": "Goal設定"}, {"start": "そうですね。 田 中 さん と ど んな ふ う に した い か って のは。", "timestamp": "01:05:59", "token": "1380", "topic": "自分ごと化"}]')
    try:
        response = format_model.generate_content(FORMAT_PROMPT + str(text))
    except Exception as e:
        raise ValueError(f"Error splitting text: {str(e)}")

    return json.loads(response.text)
