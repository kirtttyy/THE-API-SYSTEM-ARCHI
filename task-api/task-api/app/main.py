"""Application entry point: creates the FastAPI app and wires everything together."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import init_db
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # make sure the table exists when the server starts
    yield


app = FastAPI(
    title="Task API",
    version="1.0.0",
    description=(
        "A simple RESTful To-Do List API. Create, read, update and delete tasks "
        "with a title, description, due date, status and priority."
    ),
    lifespan=lifespan,
)
app.include_router(tasks.router)


# ---- Consistent error format: {"error": {"code": ..., "message": ...}} ----
@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Invalid input -> 400 Bad Request (FastAPI's default would be 422)
    parts = [
        f"{'.'.join(str(p) for p in e['loc'][1:]) or 'request'}: {e['msg']}"
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content={"error": {"code": 400, "message": "; ".join(parts)}},
    )


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    """Simple check that the server is running."""
    return {"status": "ok"}


def custom_openapi():
    """Build the OpenAPI schema and remove the unused default 422 entries."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title, version=app.version,
        description=app.description, routes=app.routes,
    )
    for path in schema["paths"].values():
        for operation in path.values():
            operation.get("responses", {}).pop("422", None)
    for name in ("HTTPValidationError", "ValidationError"):
        schema.get("components", {}).get("schemas", {}).pop(name, None)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
