"""Запуск версии агента с отдельными схемами, инструментами и маршрутами."""
from pathlib import Path
import sys
import uvicorn

draft_folder = Path(__file__).resolve().parent
project_folder = draft_folder.parent
sys.path.insert(0, str(draft_folder))
sys.path.insert(0, str(project_folder))

from main import app
from agent_style.api.agent import agent_router

app.include_router(agent_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8001)
