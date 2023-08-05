# pylint: disable=invalid-name
import os

import pytest

from .base import AsyncTestSkeleton, SyncTestSkeleton
from ..base import mark_class

__all__ = ["SyncDBTestCase", "AsyncDBTestCase"]


class RethinkDBTestTempalte:

    @classmethod
    def generate_connection_uri(cls):
        rethinkdb_host = os.environ.get('RETHINKDB_HOST', '127.0.0.1')
        return f'rethinkdb://{rethinkdb_host}', {"pool_size": 10}


@mark_class(pytest.mark.rethinkdb, pytest.mark.sync_test, pytest.mark.slow)
class SyncDBTestCase(RethinkDBTestTempalte, SyncTestSkeleton):

    pass


@mark_class(pytest.mark.rethinkdb, pytest.mark.async_test, pytest.mark.slow)
class AsyncDBTestCase(RethinkDBTestTempalte, AsyncTestSkeleton):

    use_default_loop = True
