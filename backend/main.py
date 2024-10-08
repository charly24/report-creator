from dotenv import load_dotenv

load_dotenv()

import json
import logging
import os
import traceback

import firebase_admin
import sentry_sdk
import vertexai

# from auth.api_key import verify_api_key
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from pydantic import BaseModel
from sentry_sdk import configure_scope, set_user
from sentry_sdk.integrations.flask import FlaskIntegration
from services.email_service import send_email
from services.text_processor import process_text
from werkzeug.exceptions import BadRequest, HTTPException, InternalServerError

firebase_admin.initialize_app()

logging.basicConfig(level=logging.INFO)
options.set_global_options(timeout_sec=1200, memory=512)

PROJECT_ID = "report-creator-15b64"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = Flask(__name__)
origins = [os.getenv("CORS_ORIGIN"), "http://localhost:3000"]
cors = CORS(
    app,
    resources={
        r"/*": {"origins": origins, "allow_headers": ["Content-Type", "X-API-Key"]}
    },
)
sentry_sdk.init(
    dsn="https://b75c48a6c6d0be22a068be581838f5cc@o4507768723341312.ingest.us.sentry.io/4507768727470080",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    integrations=[FlaskIntegration()],
    environment="local" if os.getenv("ENVIRONMENT") == "local" else None,
)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


class TextProcessRequest(BaseModel):
    input_text: str
    # splitting_prompt: str
    # formatting_prompt: str
    email: str


@app.post("/")
async def process_text_endpoint():
    try:
        request_data = request.get_json()
        context = TextProcessRequest(**request_data)
        set_user({"email": context.email})
        text = context.input_text
        print(f"Start: {len(text)}")
        result = await process_text(context.email, text)
        await send_email(context.email, result)
        return {"message": "Text processed and email sent successfully"}
    except ValueError as ve:
        sentry_sdk.capture_exception(ve)
        raise BadRequest(str(ve))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        traceback.print_exc()
        raise InternalServerError(f"An error occurred: {str(e)}")


@app.get("/test")
async def hoge():
    await send_email("ryo.nagaoka@gmail.com", "<h1>")
    return "test"


@app.get("/ai")
async def ai():
    from vertexai.generative_models import GenerativeModel

    model = GenerativeModel("gemini-1.5-pro")
    res = model.generate_content("日本の総理大臣は誰？")
    return res.text


@https_fn.on_request()
def on_request(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()


if __name__ == "__main__":
    app.run(debug=True, port=8000)
