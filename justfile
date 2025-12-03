set shell := ["powershell", "-c"]

setup:
    winget install -e --id astral-sh.uv
    uv python install 3.14

run:
    uv run python src/main.py
