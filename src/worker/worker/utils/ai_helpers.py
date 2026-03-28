"""
Utility functions for AI interactions.

These are pure utility functions to help format implementations
interact with AI clients without code duplication.
"""

import json
from typing import Callable, TypeVar
from celery.utils.log import get_logger

import re

T = TypeVar("T")
logger = get_logger(__name__)


def remove_think_tags(text: str) -> str:
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text


def remove_json_markdown(text: str) -> str:
    pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.search(pattern, text.strip(), flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def parse_json_response(raw_response: str) -> dict:
    """
    Clean and parse AI JSON responses.

    Handles common AI response patterns:
    - Removes <think></think> tags (DeepSeek reasoning)
    - Strips markdown code blocks (```json ... ```)
    - Parses JSON

    Args:
        raw_response: Raw text response from AI

    Returns:
        Parsed dictionary

    Raises:
        json.JSONDecodeError: If response is not valid JSON after cleaning

    Example:
        response = ai_client.chat_completion(...)
        script = parse_json_response(response)
    """
    cleaned = remove_json_markdown(remove_think_tags(raw_response))
    return json.loads(cleaned)


def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 2,
    exceptions: tuple = (Exception,),
    operation_name: str = "operation",
) -> T | None:
    """
    Retry a function with simple error handling.

    Args:
        func: Function to retry (takes no arguments)
        max_attempts: Maximum number of attempts
        exceptions: Tuple of exception types to catch and retry
        operation_name: Name of operation for logging

    Returns:
        Result of func()

    Raises:
        Last exception if all attempts fail

    Example:
        def _generate():
            response = ai_client.chat_completion(...)
            return parse_json_response(response)

        script = retry_with_backoff(
            func=_generate,
            max_attempts=3,
            exceptions=(json.JSONDecodeError, ValueError),
            operation_name="script generation"
        )
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                logger.warning(
                    f"{operation_name} attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying..."
                )
            else:
                logger.error(
                    f"{operation_name} failed after {max_attempts} attempts: {e}"
                )

    # Re-raise the last exception
    if last_exception:
        raise last_exception
    return None


def build_chat_messages(system_prompt: str, user_prompt: str) -> list[dict]:
    """
    Build OpenAI-compatible chat messages array.

    Args:
        system_prompt: System message content
        user_prompt: User message content

    Returns:
        List of message dictionaries

    Example:
        messages = build_chat_messages(
            system_prompt="You are a helpful assistant",
            user_prompt="Generate a script"
        )
        response = ai_client.chat_completion(messages=messages, ...)
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
