"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup / shutdown)."""
    print(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Whatly — Affordable WhatsApp Automation Platform for Small Businesses",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# ============================================================
# Rate limiting (slowapi)
# ============================================================
if limiter is not None:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# CORS for frontend — explicit list, not wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

# Register API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Service info."""
    return {
        "service": "whatsapp-saas-api",
        "version": "0.1.0",
        "env": settings.APP_ENV,
        "status": "ok",
    }


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "healthy"}
