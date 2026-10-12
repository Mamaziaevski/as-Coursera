import uvicorn
from fastapi import FastAPI

from mysite.admin.setup import setup_admin
from mysite.api import auth, user, search
from mysite.schemas import application, course, category, study_group, enrollment

app = FastAPI()
app.include_router(auth.auth_router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(course.router)
app.include_router(application.router)
app.include_router(study_group.router)
app.include_router(enrollment.router)
app.include_router(enrollment.group_router)
app.include_router(search.router)
setup_admin(app)




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)