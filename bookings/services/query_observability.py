"""Query counting that works with DEBUG=False (execute_wrapper)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from django.db import connection


@contextmanager
def count_db_queries() -> Iterator[dict[str, int]]:
    """Yield a dict with key ``n`` incremented for each DB execute."""
    counter = {"n": 0}

    def wrapper(execute, sql, params, many, context):
        counter["n"] += 1
        return execute(sql, params, many, context)

    with connection.execute_wrapper(wrapper):
        yield counter
