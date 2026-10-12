from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from mysite.database.schema import QuestionSchema
from mysite.chains.ai_search import search_courses

router = APIRouter(tags=["AI Search"])


@router.post("/search/")
async def answer_for_question(data: QuestionSchema):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Вопрос не может быть пустым")
    try:
        return await run_in_threadpool(search_courses, question)
    except ImportError:
        raise HTTPException(status_code=503, detail="Установи зависимости из req-ai.txt")
    except Exception:
        raise HTTPException(status_code=503, detail="ИИ-поиск недоступен. Проверь Ollama и скачанные модели")
