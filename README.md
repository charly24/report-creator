# Text Formatting Tool

This tool provides a system for formatting long texts, splitting them into appropriate sizes, and sending the formatted results via email. It consists of a React frontend and a Python backend, deployed on Google Cloud Platform (GCP) using Cloud Functions.

## Features

- Split long texts into appropriate sizes
- Format each split text section using Google Gemini Pro 1.5
- Combine formatted sections and send via email
- Customizable prompts for text splitting and formatting
- User authentication with API keys
- Designed for internal use by approximately 50 users

## Architecture

- Frontend: React
- Backend: Python on Google Cloud Functions
- LLM: Google Gemini Pro 1.5 (free tier)
- Logging: Cloud Logging

## Setup

### Prerequisites

- Google Cloud Platform account
- Node.js and npm for frontend development
- Python 3.x for backend development
- gcloud CLI tool installed and configured

### Deployment

1. Clone this repository:

   ```
   git clone https://github.com/your-repo/text-formatting-tool.git
   cd text-formatting-tool
   ```

2. Set up GCP credentials:

   ```
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Deploy the Cloud Function:

   ```
   gcloud functions deploy text-formatting-function \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated
   ```

4. Deploy the frontend (assuming you're using Firebase Hosting):
   ```
   firebase deploy --only hosting
   ```

## Configuration

### API Keys

API keys are managed securely using Google Secret Manager. To set up a new API key:

1. Create a secret:

   ```
   gcloud secrets create api-key --replication-policy="automatic"
   ```

2. Add a new version with the API key:

   ```
   echo -n "your-api-key" | gcloud secrets versions add api-key --data-file=-
   ```

3. Grant the Cloud Function access to the secret:
   ```
   gcloud secrets add-iam-policy-binding api-key \
     --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

Update the `config.py` file in the backend directory to use Secret Manager:

```python
from google.cloud import secretmanager

def access_secret_version(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

API_KEY = access_secret_version("api-key")
```

## Usage

1. Access the tool through the deployed URL.
2. Enter the following in the frontend interface:

   - Input text
   - Splitting prompt
   - Formatting prompt
   - Email address
   - User API key

3. Click "Process" to start the text formatting.

4. The formatted text will be sent to the specified email address.

## Error Handling

- The frontend displays error messages with instructions to wait and try again later if the Gemini Pro API rate limit is reached.
- All errors are logged in Cloud Logging for monitoring and debugging.

## Performance Considerations

- The tool is designed for internal use by approximately 50 users.
- Processing time is expected to be under 10 minutes per request.
- Due to Gemini Pro free tier limitations, concurrent usage may result in errors. Users are notified to try again later in such cases.

## Logging

All used prompts and errors are logged in Cloud Logging. Access logs through the GCP Console or using the gcloud command:

```
gcloud functions logs read text-formatting-function
```

## Development

### Frontend

Navigate to the `frontend` directory and run:

```
npm install
npm start
```

### Backend

Navigate to the `backend` directory and run:

```
pip install -r requirements.txt
python main.py
```

## Deployment from Local Environment

Ensure you have the gcloud CLI installed and configured. Then run:

```
./deploy.sh
```

This script will build the frontend and deploy both the frontend and backend to GCP.

## Language Support

The tool is designed for Japanese language support only.

## Support

For any issues or questions, please contact the internal development team.
