"""
    Errors handling module

"""


import logging
from typing import Any
from fastapi import HTTPException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def error_handling(code: str, message: str, payload : Any = None) -> None:
    """
    Errors handling

    """

    match code:
        case 'bad_request':
            logger.info('%s', message)
            raise HTTPException(status_code = 400, detail = message)

        case 'unauthorized':
            logger.info('%s', message)
            raise HTTPException(status_code = 401, detail = message, headers = payload)

        case 'forbidden':
            logger.info('%s', message)
            raise HTTPException(status_code = 403, detail = message)

        case 'not_found':
            logger.info('%s', message)
            raise HTTPException(status_code = 404, detail = message)

        case 'validation_error':
            logger.info('%s', message)
            raise HTTPException(status_code = 422, detail = message)
