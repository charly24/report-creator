from datetime import datetime
from services.split_service import split_text
from services.text_splitter import pares_segments
from services.format_service import format_text

async def process_text(input_text: str) -> str:
    # Step 1: Split the text
    split_segments = await split_text(input_text)
    print(split_segments)

    # Step 2: Format each split part
    segments = await pares_segments(input_text, split_segments)
    formatted_parts = []
    for segment in segments:
        formatted_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(f"{formatted_time} {segment['topic']} start -> {len(segment['text'])}")
        formatted_part = await format_text(segment['text'])
        title = f"{segment['topic']} ({segment['timestamp']}~)"
        html_text = formatted_part.replace('\n', '<br>')
        text = f"<h2>{title}</h2><p>{html_text}</p>"
        formatted_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        print(f"{formatted_time} {segment['topic']} end -> {len(text)}")
        formatted_parts.append(text)
    
    # Step 3: Combine formatted parts
    result = "\n\n".join(formatted_parts)
    
    return result