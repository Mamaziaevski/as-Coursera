import uvicorn
from fastapi import FastAPI

from mysite.admin.setup import setup_admin
from mysite.api import auth, user




app = FastAPI()
app.include_router(auth.auth_router)
app.include_router(user.router)

setup_admin(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)