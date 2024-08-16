from datetime import datetime

import sentry_sdk
import tiktoken
from services.format_service import format_text
from services.split_service import analyze_text
from services.text_splitter import pares_segments

encoding = tiktoken.get_encoding("cl100k_base")


def track_input_length(email, input_text):
    text_length = len(input_text)

    # SentryのメトリクスにGaugeとして値を送信
    sentry_sdk.metrics.gauge(
        key="input_text_length", value=text_length, tags={"email": email}
    )


async def process_text(email: str, input_text: str) -> str:
    track_input_length(email, input_text)
    # transaction = sentry_sdk.Sentry.startTransaction({ name: "アプリ起動" });
    # Step 1: Split the text
    analyzed = await analyze_text(input_text)
    print(analyzed)
    if len(analyzed["topics"]) >= 12:
        raise ValueError("分割に失敗しました。再実行してください。")

    # Step 2: Format each split part
    segments = await pares_segments(input_text, analyzed["topics"])
    formatted_parts = []
    for segment in segments:
        formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f"{formatted_time} {segment['topic']} start -> {segment['token']} token")
        formatted_part = await format_text(segment["text"], analyzed["characters"])
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

    return result
