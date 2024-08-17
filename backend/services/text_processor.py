from datetime import datetime

import sentry_sdk
import tiktoken
from services.format_service import format_text
from services.split_service import analyze_text
from services.split_detail_service import split_detail

encoding = tiktoken.get_encoding("cl100k_base")


def track_input_length(email, input_text):
    text_length = len(input_text)

    # SentryのメトリクスにGaugeとして値を送信
    sentry_sdk.metrics.gauge(
        key="input_text_length", value=text_length, tags={"email": email}
    )


async def process_text(email: str, input_text: str) -> str:
    if len(input_text) < 10000:
        raise ValueError(
            "レポート用文章でこの文字数は少なすぎます。セッションの文字起こし内容を入力してください。"
        )

    track_input_length(email, input_text)
    # transaction = sentry_sdk.Sentry.startTransaction({ name: "アプリ起動" });
    # Step 1: Split the text
    characters, raw_topics = await analyze_text(input_text)
    topics = []
    print(
        "topics",
        [{k: v for k, v in topic.items() if k != "text"} for topic in raw_topics],
    )
    for topic in raw_topics:
        # 16k以上となると出力できないので分割する
        if topic["token"] > 16000:
            print(f"詳細分割: {topic['topic']} ({topic['token']} tokens)")

            tmp = await split_detail(topic["text"])
            tmp[0]["topic"] = topic["topic"]
            topics.extend(tmp)
        else:
            topics.append(topic)

    if len(raw_topics) != len(topics):
        print(
            "updated topics",
            [{k: v for k, v in topic.items() if k != "text"} for topic in topics],
        )

    if len(topics) >= 15:
        raise ValueError("分割に失敗しました。再実行してください。")

    # Step 2: Format each split part
    formatted_parts = []
    prev_topic = ""
    for topic in topics:
        formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(
            f"{formatted_time} {topic['topic'] or prev_topic} start -> {topic['token']} token"
        )
        formatted_part = await format_text(topic["text"], characters)
        if prev_topic == topic["topic"] or topic["topic"] == "":
            title = ""
        else:
            title = f"<h2>{topic['topic']} ({topic['timestamp']}~)</h2>"
        html_text = formatted_part.replace("\n", "</p><p>")
        text = f"{title}<p>{html_text}</p>"
        formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(
            f"{formatted_time} {topic['topic'] or prev_topic} end -> {len(encoding.encode(text))} token"
        )
        formatted_parts.append(text)
        if topic["topic"] != "":
            prev_topic = topic["topic"]

    # Step 3: Combine formatted parts
    result = "\n\n".join(formatted_parts)

    result = f"""
<h1>セッションレポート</h1>
<h2>1.クライアントが、コーチングを受ける背景やキャリアの状況</h2>
<h2>2.なにが新しい挑戦を妨げているのか。</h2>
<h2>3.なぜずっと同じ状態に居続けているのか。</h2>
<h2>4.なぜ同じ状況にいることを許容しているのか。</h2>
<h1>セッションログ</h1>
{result}"""

    return result
