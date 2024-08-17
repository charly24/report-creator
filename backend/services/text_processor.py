from datetime import datetime

import sentry_sdk
import tiktoken
from services.format_service import format_text
from services.split_service import analyze_text

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
    characters, segments = await analyze_text(input_text)
    if len(segments) >= 12:
        raise ValueError("分割に失敗しました。再実行してください。")
    print(
        characters,
        [{k: v for k, v in segment.items() if k != "text"} for segment in segments],
    )

    # Step 2: Format each split part
    formatted_parts = []
    for segment in segments:
        formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f"{formatted_time} {segment['topic']} start -> {segment['token']} token")
        formatted_part = await format_text(segment["text"], characters)
        title = f"{segment['topic']} ({segment['timestamp']}~)"
        html_text = formatted_part.replace("\n", "<br>")
        text = f"<h2>{title}</h2><p>{html_text}</p>"
        formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(
            f"{formatted_time} {segment['topic']} end -> {len(encoding.encode(text))} token"
        )
        formatted_parts.append(text)

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
