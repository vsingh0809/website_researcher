# app/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class ResearchAppException(Exception):
    """Base exception for our business domain."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class SearchFailedException(ResearchAppException):
    pass

class CrawlFailedException(ResearchAppException):
    pass

class AISynthesisException(ResearchAppException):
    pass

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ResearchAppException)
    async def global_research_exception_handler(request: Request, exc: ResearchAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message}
        )