from dotenv import load_dotenv

load_dotenv()

import os
import logging
import traceback

import firebase_admin

# from auth.api_key import verify_api_key
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from pydantic import BaseModel
from services.email_service import send_email
from services.text_processor import process_text
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

firebase_admin.initialize_app()

app = Flask(__name__)
origins = [os.getenv("CORS_ORIGIN"), "http://localhost:3000"]
cors = CORS(
    app,
    resources={
        r"/*": {"origins": origins, "allow_headers": ["Content-Type", "X-API-Key"]}
    },
)


class TextProcessRequest(BaseModel):
    input_text: str
    # splitting_prompt: str
    # formatting_prompt: str
    email: str


@app.post("/")
async def process_text_endpoint():
    try:
        request_data = request.get_json()
        text_request = TextProcessRequest(**request_data)
        text = text_request.input_text
        print(f"Start: {len(text)}")
        result = await process_text(text)
        await send_email(text_request.email, result)
        return {"message": "Text processed and email sent successfully"}
    except ValueError as ve:
        raise BadRequest(str(ve))
    except Exception as e:
        traceback.print_exc()
        raise InternalServerError(f"An error occurred: {str(e)}")


@app.get("/test")
async def hoge():
    await send_email("ryo.nagaoka@gmail.com", "test")
    return "test"


options.set_global_options(timeout_sec=600)


@https_fn.on_request()
def on_request(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=8000)
