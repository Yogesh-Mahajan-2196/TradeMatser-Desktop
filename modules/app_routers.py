from fastapi import APIRouter
from .dashboard.app_router import dashboard_router
from .auth.app_router import auth_router
from .parties.app_router import parties_router
from .products.app_router import product_router
from .purchase.app_router import purchase_router
from .reports.app_router import reports_router
from .sell.app_router import sell_router
from .transpotation.app_router import transpotation_router
from .expenses.app_router import expense_router
from .payments.app_router import payment_router
from .party_ledger.app_router import party_leadger_router

apps_router = APIRouter()
apps_router.include_router(dashboard_router)
apps_router.include_router(auth_router)
apps_router.include_router(parties_router)
apps_router.include_router(product_router)
apps_router.include_router(purchase_router)
apps_router.include_router(reports_router)
apps_router.include_router(sell_router)
apps_router.include_router(transpotation_router)
apps_router.include_router(expense_router)
apps_router.include_router(payment_router)
apps_router.include_router(party_leadger_router)