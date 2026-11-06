from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.api_routers import api_routers
from modules.app_routers import apps_router
from utils.daily_report_schedular import start_scheduler
# from testgen.api_testgen import CaptureMiddleware
# from testengine.capture.install import install
from utils.daily_report_schedular import scheduler, start_scheduler
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

# install(app)

app.include_router(api_routers)
app.include_router(apps_router)
# app.add_middleware(CaptureMiddleware)