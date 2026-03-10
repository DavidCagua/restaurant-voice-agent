"""
Retry utility with exponential backoff for handling transient errors.

Unit-testable retry logic for external API calls.
"""

import time
import random
from typing import Callable, TypeVar, Optional, Tuple
from functools import wraps

T = TypeVar('T')

# Transient error status codes
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}
TRANSIENT_EXCEPTIONS = (ConnectionError, TimeoutError, OSError)


def is_transient_error(status_code: Optional[int] = None, exception: Optional[Exception] = None) -> bool:
    """
    Check if an error is transient and should be retried.
    
    Args:
        status_code: HTTP status code (if available)
        exception: Exception that was raised (if available)
    
    Returns:
        True if the error is transient and should be retried
    """
    if status_code and status_code in TRANSIENT_STATUS_CODES:
        return True
    if exception and isinstance(exception, TRANSIENT_EXCEPTIONS):
        return True
    return False


def exponential_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> float:
    """
    Calculate exponential backoff delay with optional jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
    
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    if jitter:
        # Add up to 25% random jitter
        jitter_amount = delay * 0.25 * random.random()
        delay = delay + jitter_amount
    return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on: Optional[Callable[[Optional[int], Optional[Exception]], bool]] = None
) -> Callable:
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (total attempts = max_retries + 1)
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        retry_on: Custom function to determine if error should be retried.
                 Takes (status_code, exception) and returns bool.
                 Defaults to is_transient_error.
    
    Returns:
        Decorated function that retries on transient errors
    """
    if retry_on is None:
        retry_on = is_transient_error
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            last_status_code = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # If function returns a tuple (result, status_code), extract both
                    if isinstance(result, tuple) and len(result) == 2:
                        value, status_code = result
                        if status_code and not (200 <= status_code < 300):
                            if retry_on(status_code, None) and attempt < max_retries:
                                last_status_code = status_code
                                delay = exponential_backoff_delay(attempt, base_delay, max_delay)
                                time.sleep(delay)
                                continue
                        return result
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this error
                    if retry_on(None, e) and attempt < max_retries:
                        delay = exponential_backoff_delay(attempt, base_delay, max_delay)
                        time.sleep(delay)
                        continue
                    else:
                        # Don't retry - re-raise the exception
                        raise
            
            # If we exhausted retries, raise the last exception
            if last_exception:
                raise last_exception
            if last_status_code:
                raise RuntimeError(f"Request failed with status {last_status_code} after {max_retries + 1} attempts")
            
            # Should not reach here, but just in case
            raise RuntimeError(f"Function {func.__name__} failed after {max_retries + 1} attempts")
        
        return wrapper
    return decorator


def async_retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on: Optional[Callable[[Optional[int], Optional[Exception]], bool]] = None
) -> Callable:
    """
    Decorator for retrying async function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (total attempts = max_retries + 1)
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        retry_on: Custom function to determine if error should be retried.
                 Takes (status_code, exception) and returns bool.
                 Defaults to is_transient_error.
    
    Returns:
        Decorated async function that retries on transient errors
    """
    if retry_on is None:
        retry_on = is_transient_error
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            import asyncio
            last_exception = None
            last_status_code = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # If function returns a tuple (result, status_code), extract both
                    if isinstance(result, tuple) and len(result) == 2:
                        value, status_code = result
                        if status_code and not (200 <= status_code < 300):
                            if retry_on(status_code, None) and attempt < max_retries:
                                last_status_code = status_code
                                delay = exponential_backoff_delay(attempt, base_delay, max_delay)
                                await asyncio.sleep(delay)
                                continue
                        return result
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this error
                    if retry_on(None, e) and attempt < max_retries:
                        delay = exponential_backoff_delay(attempt, base_delay, max_delay)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Don't retry - re-raise the exception
                        raise
            
            # If we exhausted retries, raise the last exception
            if last_exception:
                raise last_exception
            if last_status_code:
                raise RuntimeError(f"Request failed with status {last_status_code} after {max_retries + 1} attempts")
            
            # Should not reach here, but just in case
            raise RuntimeError(f"Function {func.__name__} failed after {max_retries + 1} attempts")
        
        return wrapper
    return decorator
