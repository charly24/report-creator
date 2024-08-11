import tiktoken
from typing import List, Dict

encoding = tiktoken.get_encoding("cl100k_base")


async def pares_segments(input_text, segments) -> List[Dict[str, str]]:
    # 結果を格納するリスト
    result = []

    # 各セグメントの開始位置を見つける
    for i, segment in enumerate(segments):
        start = segment["start"]
        start_index = input_text.find(start)

        if start_index == -1:
            # startが見つからない場合はスキップ
            continue

        # 次のセグメントの開始位置を見つける（最後のセグメントの場合は文書の最後まで）
        if i < len(segments) - 1:
            next_start = segments[i + 1]["start"]
            end_index = input_text.find(next_start)
            if end_index == -1:
                end_index = len(input_text)
        else:
            end_index = len(input_text)

        # セグメントのテキストを抽出
        segment_text = input_text[start_index:end_index].strip()

        # 結果に追加
        result.append(
            {
                "text": segment_text,
                "timestamp": segment["timestamp"],
                "topic": segment["topic"],
                "token": len(encoding.encode(segment_text)),
            }
        )

    return result
