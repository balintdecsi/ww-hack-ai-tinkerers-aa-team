# Comics Factory

## Project Description
Comics Factory is a demo application created for a hackathon. Its purpose is to showcase an immersive experience for conversational AI solutions, leveraging the power of **Anam**, **Blackbox**, **ElevenLabs**, and **Gemini** APIs to create an intelligent workflow.

## Setup Instructions

### 1. Python Version
Ensure you have Python 3.11 or higher installed.

### 2. Install `uv` Package Manager
This project uses `uv` for dependency management. If you don't have `uv` installed, you can install it using pip:
```bash
pip install uv
```

### 3. Environment Variables
API keys and other sensitive information are loaded from a `.env` file.
Create a `.env` file in the root directory of the project by copying the `.env.example` file:
```bash
cp .env.example .env
```
Now, open the newly created `.env` file and replace the placeholder values with your actual API keys. For example:
```
ANAM_API_KEY=your_anam_api_key_here
BLACKBOX_API_KEY=your_blackbox_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Install Dependencies
With `uv` installed, navigate to the project's root directory and install the required dependencies:
```bash
uv pip install -r requirements.txt
```

### 5. Run the Flask Application
After installing dependencies, you can run the Flask application locally:
```bash
flask run
```

The application will typically be available at `http://127.0.0.1:5000/`.

### Available Routes
- `/`: Returns "Hello, World!"
- `/health`: Returns `{"status": "ok"}`