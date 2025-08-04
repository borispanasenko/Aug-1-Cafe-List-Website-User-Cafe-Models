import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.app_routers.__init__ import router

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import time


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = FastAPI(title="TripAdvisor-like API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63343"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Response: status {response.status_code}, time {process_time:.2f}s")
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise


app.add_middleware(LoggingMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f'HTTP exception: {exc.status_code} - {exc.detail} at {request.url.path}')
    return JSONResponse(
        status_code=exc.status_code,
        content={'error_code': exc.status_code, 'message': exc.detail, 'path': str(request.url.path)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f'Server error: {str(exc)} at {request.url.path}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'error_code': 500, 'message': 'Internal server error. Please try again later.',
                 'path': str(request.url.path)}
    )

app.include_router(router)
