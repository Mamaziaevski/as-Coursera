from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mysite.api.auth import get_current_user
from mysite.database.db import get_db
from mysite.database.model import User
from mysite.schemas.agent_schema import AgentInputSchema, AgentOutputSchema
from mysite.chains.agent_chain import run_agent
from mysite.chains.agent_tools import tool_schemas


agent_router = APIRouter(prefix='/agent', tags=['AI Agent'])


@agent_router.post('/chat/', response_model=AgentOutputSchema)
async def agent_chat(data: AgentInputSchema,
                     db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return await run_agent(data.message, db, current_user, list(tool_schemas))


@agent_router.post('/register/', response_model=AgentOutputSchema)
async def agent_register(data: AgentInputSchema, db: AsyncSession = Depends(get_db)):
    return await run_agent(data.message, db, None, ['register_user'])
