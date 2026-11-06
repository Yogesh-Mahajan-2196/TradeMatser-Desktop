from fastapi import APIRouter
from .auth.api_router import auth_router
from .purchase.api_router import purchase_router
from .products.api_router import product_router
from .parties.api_router import parties_router
from .reports.api_router import report_router
from .sell.api_router import sell_router
from .transpotation.api_router import transpotation_router
from .expenses.api_router import expense_router

api_routers = APIRouter(
    prefix="/api"
)

api_routers.include_router(auth_router)
api_routers.include_router(purchase_router)
api_routers.include_router(product_router)
api_routers.include_router(parties_router)
api_routers.include_router(report_router)
api_routers.include_router(sell_router)
api_routers.include_router(transpotation_router)
api_routers.include_router(expense_router)