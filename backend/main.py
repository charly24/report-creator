from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from auth.api_key import verify_api_key
from services.text_processor import process_text
from services.email_service import send_email

app = FastAPI()

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
        # with open('asada.txt', 'r', encoding='utf-8') as file:
        #     text = file.read()
        #     print(len(text))
        text = request.input_text
        result = await process_text(
            text
            # request.input_text,
            # request.splitting_prompt,
            # request.formatting_prompt
        )
        print(result)
        send_email(request.email, result)
        return {"message": "Text processed and email sent successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)