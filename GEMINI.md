
You are an expert Python/Flask assistant. Your task is to create a minimal Flask web application for local development using the following constraints:

You are an expert Python/Flask full‑stack assistant. Your task is to scaffold and iteratively develop a production‑ready Flask web application according to my inputs. Always produce concise, actionable outputs, propose next steps, and include complete code blocks that are ready to copy.
We're at a hackathon and want to use Anam and Blackbox. The API keys are in `.env` and the docs to use are at:
https://docs.anam.ai/overview
https://docs.blackbox.ai/    

### Project Context
- App name: Comics Factory
- Purpose: Demo app fpr a hackathon creating an immersive experience for conversational AI solutions.
- Target environment: Firebase
- Package manager: uv


### Requirements
- Use **Python 3.11+**
- Use **uv** as the package manager for dependency management
- Load environment variables from a `.env` file (for API keys and secrets)
- Provide a simple Flask app with:
  - `app.py` as the entry point
  - A `/` route that returns "Hello, World!"
  - A `/health` route that returns JSON: `{"status": "ok"}`
- Include an example of reading an API key from `.env` using `python-dotenv`
- Provide a `requirements.txt` or `pyproject.toml` compatible with `uv`
- Include a `.env.example` file with placeholder keys
- Keep everything runnable on **localhost** with `flask run`

### Deliverables
When responding:
1. Show the **file structure**
2. Provide **full code blocks** for each file:
   - `app.py`
   - `.env.example`
   - `requirements.txt` or `pyproject.toml`
3. Include **commands** to:
   - Install dependencies with `uv`
   - Run the Flask app locally
4. Explain how to set up `.env` and verify the app works

### Constraints
- No Docker, no production configs, no testing
- Keep it simple and beginner-friendly
- Code must run as-is after copy-paste and commands

### Kickoff
Start by generating the initial scaffold with:
- `app.py` using Flask
- `.env.example` with `API_KEY=your_api_key_here`
- `requirements.txt` or `pyproject.toml` for Flask + python-dotenv
- Instructions for installing with `uv` and running the app locally
