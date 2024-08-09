from dotenv import load_dotenv
load_dotenv()

import logging
import traceback
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth.api_key import verify_api_key
from services.text_processor import process_text
from services.email_service import send_email

app = FastAPI()

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextProcessRequest(BaseModel):
    input_text: str
    # splitting_prompt: str
    # formatting_prompt: str
    email: str

@app.post("/process_text")
async def process_text_endpoint(
    request: TextProcessRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        # await send_email(request.email, '<h2>test</h2><p>ほげら</p><h2>test2</h2><p>ぷぎゃ</p>')
        # 1 / 0
        # with open('asada.txt', 'r', encoding='utf-8') as file:
        #     text = file.read()
        #     print(len(text))
        text = request.input_text
        print(f"Start: {len(text)}")
        result = await process_text(
            text
            # request.input_text,
            # request.splitting_prompt,
            # request.formatting_prompt
        )
        await send_email(request.email, result)
        return {"message": "Text processed and email sent successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # traceback.print_stack()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    import asyncio
    import multiprocessing
    logging.basicConfig(level=logging.INFO)
    multiprocessing.set_start_method("fork")
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
