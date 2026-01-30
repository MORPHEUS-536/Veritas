from fastapi import FastAPI
from routers import students, assessments, dashboard, general

app = FastAPI(title="Evolve AI Backend")

app.include_router(general.router)
app.include_router(students.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
