import os

from vertexai.generative_models import GenerativeModel


model = GenerativeModel(model_name=os.getenv("GEMINI_MODEL_PRO"))

FORMAT_PROMPT = """
# 命令文
あなたは議事録作成のプロフェッショナルです。コーチングセッションの文字起こしデータを、指定された制約条件に厳密に従って整形してください。整形は必ず入力文の最初から最後まで連続的に行い、途中で中断しないでください。

# 前提条件
・入力文の内容は、コーチングセッションの文字起こしデータです。
・AIによる文字起こしのため、一部に誤りが含まれている可能性があります。

# 制約条件
1. 文章の整形:
   - 文意や内容を変えずに、誤りを修正しつつ整形してください。
   - 不要な半角スペースは削除してください。
   - ケバ取りを行ってください。
   - 文脈から不明瞭な部分や聞き取りにくい箇所は [不明瞭] と表記し、可能な限り文脈から推測して括弧内に記入すること。

2. 発言者の表記:
   - コーチを"コ: "、クライアントを"ク: "として表記してください。
   - 文中に出てくるクライアントの名前は"登場人物"も参考にして"Xさん"に変換してください。これは個人情報保護のため非常に重要です。
   - クライアントを紹介してくれた方の名前は"[紹介者]"に変換してください

3. 発言の整形:
   a. 同じ人が連続して話している場合、1行にまとめてください。
   b. 長い発言でトピックが変わる場合、2つ改行を入れて読みやすくしてください。その際、最初以外には「コ: 」「ク: 」は不要です。
   c. 文脈を理解する上で重要な「はい」「うん」「うーん」以外の相槌は削除してください。
   d. 引用表現は「」で囲んでください。
   e. 相手に確認を促す文章の文末には"？"を追加してください。
   f. 重要: フィラーワードを除いた上で、すべての実質的な内容を省略せずに文字起こしすること。

4. 不要な表現の削除:
   - 「はい。」「うん。」などの不要な相槌や文字起こしの誤りと思われる表現は削除してください。
   - ただし、クライアントの思考過程を示す重要な表現は残してください。

5. 頻出キーワードの注意点:
   - "want to"（誤: ウォントトゥー、モントトゥー）
   - "ビリーフシステム"（誤: ビリフシステム）

6. 完全性の確保:
   - 入力文の全内容を必ず整形してください。
   - トークン数が不足する場合は、その旨を表示し、処理可能な範囲まで整形してください。
   - 会議の全内容を漏れなく文字起こしすること。省略や要約は避け、全ての発言を記録すること。

7. フィラーワードと口語表現の扱い:
    a. 上記3.fで指定したフィラーワードは文字起こしから除外すること。
    b. ただし、フィラーワード以外の口語表現（例：「～じゃない？」「～だよね」）はそのまま記録すること。
    c. フィラーワードの除外によって文の意味が変わらないよう注意すること。
    d. 話者の特徴的な話し方や強調のための繰り返しは、文脈に応じて適切に判断し記録すること。

8. 出力形式:
   - 整形後のテキストのみを出力してください。
   - サンプル文や指示自体は出力しないでください。

この制約条件に従って、入力文を最初から最後まで確実に整形してください。整形プロセスが中断しないよう注意し、完全な整形結果を提供してください。

# 出力サンプル
コ: (コーチの発言内容)

(発言内容が長い場合は制約条件に応じて分割)

ク: (クライアントの発言内容)
...

# 登場人物
クライアント: #クライアント#
コーチ: #コーチ#
紹介者: #紹介者#

# 入力文
"""


async def format_text(text: str, characters, cnt: int = 0) -> str:
    try:
        prompt = (
            FORMAT_PROMPT.replace("#クライアント#", characters["client"])
            .replace("#コーチ#", characters["coach"])
            .replace("#紹介者#", characters["introducer"])
        )
        response = model.generate_content(prompt + str(text))
        return response.text
    except Exception as e:
        if cnt < 3 and "429" not in str(e):
            print(
                f"Format時にエラーが発生したので再実行します({cnt + 1}回目): {str(e)}"
            )
            return await format_text(text, characters, cnt + 1)
        raise e
