"""
    Errors handling module

"""


import logging
from fastapi import HTTPException, status


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def error_handling(code: str, message: str, payload: dict = None):
    match code:
        case 'validation_error':
            logger.info('%s', message)
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = message
            )

        case 'unauthorized':
            logger.info('%s', message)
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = message,
                headers = payload
            )
        
        case 'not_found':
            logger.info('%s', message)
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = message
            )
        
        case 'forbidden':
            logger.info('%s', message)
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = message
            )

        case 'bad_request':
            logger.info('%s', message)
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = message
            )