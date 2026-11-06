from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

reports_router = APIRouter(
    tags = ["Reports"]
)
templates=Jinja2Templates(directory="templates")