set shell := ["powershell", "-c"]

setup:
    #!powershell
    winget install -e --id astral-sh.uv
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    uv python install 3.14
    uv venv
    uv sync

run:
    uv run python src/main.py

package:
    git archive -o news-monitor.zip HEAD
