import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError

from ttsclient.const import LOGGER_NAME


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:  # type: ignore
                logging.getLogger(LOGGER_NAME).error(f"RequestValidationError: {str(exc)}")
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}
                raise HTTPException(status_code=422, detail=detail)
            except HTTPException as exc:
                raise exc
            except Exception as exc:
                import traceback

                logging.getLogger(LOGGER_NAME).error(f"Exception: {str(exc)}")
                logging.getLogger(LOGGER_NAME).error(f"Exception tb: {traceback.format_exc()}")
                try:
                    body = await request.body()
                    detail = {"errors": str(exc), "body": body.decode()}
                    raise HTTPException(status_code=422, detail=detail)
                except Exception as exc2:
                    detail = {
                        "errors": str(exc),
                        "errors2": str(exc2),
                    }
                    raise HTTPException(status_code=422, detail=detail)

        return custom_route_handler
