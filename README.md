# Comics Factory

A Flask application creating immersive experiences for conversational AI solutions using Anam and Blackbox APIs.

## Setup

1.  **Install `uv` (if not installed):**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r pyproject.toml --all-extras
    # OR if uv sync is available/preferred
    uv sync
    ```

3.  **Environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys
    ```

4.  **Database:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

5.  **Run (Dev):**
    ```bash
    flask run
    ```

## Testing
```bash
pytest
```
