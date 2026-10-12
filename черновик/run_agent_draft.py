r"""Запуск черновика без редактирования main.py. Выполнять из папки проекта.

PowerShell:
    .\.venv\Scripts\python.exe .\черновик\run_agent_draft.py
"""
import importlib.util
from pathlib import Path
import sys

import uvicorn

project = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project))

from main import app

spec = importlib.util.spec_from_file_location("agent_draft", Path(__file__).with_name("agent_draft.py"))
agent = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = agent
spec.loader.exec_module(agent)
app.include_router(agent.router)

if __name__ == "__main__":
    # Другой порт позволяет держать обычный проект на 8000, а черновик на 8001.
    uvicorn.run(app, host="127.0.0.1", port=8001)
