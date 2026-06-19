from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="aQuickRescue API")

# Allow local development CORS (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {"status": "ok", "message": "aQuickRescue API"}


@app.get("/health", tags=["Health"])
async def health():
    """Simple health endpoint used by containers and orchestrators."""
    return {"status": "healthy"}


# Import service modules (if they have startup side-effects). Keep imports
# in try/except so the app still starts if a module has unmet optional deps.
try:
    # Import modules to ensure they can be loaded during startup
    from .services import fhir_service  # noqa: F401
except Exception:
    # If imports fail (missing deps during local dev), don't crash the app here.
    pass

