import ast
import json
import mock
import unittest
from contextlib import suppress
from uuid import uuid4

import arrow

from dq.database import commit_scope, save_to_database
from dq.orm import Cache
from tests.models import Table2, User, UserType


class TestORM(unittest.TestCase):

    def tearDown(self):
        with suppress(Exception), commit_scope() as session:
            session.query(Table2).delete()
            session.query(User).delete()
            if Cache._instance:
                Cache._instance.flushall()

    def test_string(self):
        t2 = Table2(id=1, key=1, key2=1, user_type=UserType.admin,
                    created_at=arrow.get('2017-10-21'))
        t2_str = str(t2)
        assert t2_str.startswith('<Table2 ')
        assert ast.literal_eval(t2_str[8:-1]) == {
            'id': 1,
            'user_uuid': None,
            'user_type': 'admin',
            'key2': True,
            'created_at': 1508544000,
        }

    def test_cache_key(self):
        assert Table2.cache_key('uuid', '123') == 'dqpy.cache.table2.uuid.123'
        k2 = Table2.cache_key('id', 123, contains_deleted=True,
                              contains_empty=True)
        assert k2 == 'dqpy.cache.table2.id.123.del.empty'

    def test_cached(self):
        t2 = Table2(id=999, user_uuid=str(uuid4()), key=1, key2=1,
                    user_type=UserType.regular)
        save_to_database(t2)

        key = 'dqpy.cache.table2.id.999'
        assert not Cache.get(key)

        t2 = Table2.get(999)
        assert t2.key == 1
        assert Cache.get(key)
        with commit_scope() as session:
            session.query(Table2).delete()
        t2 = Table2.get(999)
        assert t2.key == 1

    def test_cache_error(self):
        Cache._instance = 123
        assert not Cache.get('cornell')
        Cache.set('cornell', '#1', 123)
        Cache._instance = None

    @mock.patch('dq.config.Config.get')
    def test_cache_broken(self, mock_cfg):
        mock_cfg.return_value = {'port': 1234}
        Cache._instance = None
        Cache._attempted = None
        assert not Cache.instance()
        assert Cache._attempted
        assert not Cache.get('cornell')
        Cache.set('cornell', '#1', 123)
        Cache._attempted = None

    @mock.patch('dq.config.Config.get')
    def test_cache_none(self, mock_cfg):
        mock_cfg.return_value = None
        Cache._instance = None
        Cache._attempted = None
        assert not Cache.instance()
        assert Cache._attempted
        assert not Cache.get('cornell')
        Cache.set('cornell', '#1', 123)
        Cache._attempted = None

    def test_to_dict(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                    user_type=UserType.regular, created_at=now)

        t2_dict = t2.to_dict()
        t2_inflate = t2.inflate_to_dict()
        assert t2_inflate == t2_dict
        assert t2_dict == {
            'id': 1,
            'user_uuid': uuid,
            'user_type': 'regular',
            'key2': True,
            'created_at': now.timestamp,
        }

    def test_to_json(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                    user_type=UserType.regular, created_at=now)
        t2_json = t2.to_json()
        assert json.loads(t2_json) == {
            'id': 1,
            'user_uuid': uuid,
            'user_type': 'regular',
            'key2': True,
            'created_at': now.timestamp,
        }

    def test_from_dict(self):
        uuid = str(uuid4())
        now = arrow.get()
        t2_dict = {
            'id': 1,
            'user_uuid': uuid,
            'key': 1,
            'key2': 1,
            'created_at': now.timestamp,
        }
        t2 = Table2.from_dict(t2_dict)
        assert t2.created_at == arrow.get(now.timestamp)
        assert not t2.key2

    def test_get_by(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid)
        save_to_database(t2)

        t2 = Table2.get_by('user_uuid', uuid)
        assert t2.id == 1

    def test_get_by_empty(self):
        t2 = Table2(id=1, user_uuid=str(uuid4()))
        save_to_database(t2)
        assert not Table2.get_by('user_uuid', None)

    def test_get_multi(self):
        uuid = str(uuid4())
        t21 = Table2(id=1, user_uuid=uuid, key=1, key2=1)
        t22 = Table2(id=2, user_uuid=uuid, key=1, key2=2)
        t23 = Table2(id=3, user_uuid=uuid, key=1, key2=3)
        t24 = Table2(id=4, user_uuid=uuid, key=1, key2=4)
        t25 = Table2(id=5, user_uuid=uuid, key=1, key2=5)
        save_to_database([t21, t22, t23, t24, t25])

        results = Table2.get_multi('key', 1, 'key2', offset=2, limit=2)
        assert len(results) == 2
        assert results[0].key2 == 3
        assert results[1].key2 == 2

        results = Table2.get_multi('key', 1, 'key2', desc=False, limit=7)
        assert len(results) == 5
        assert results[0].key2 == 1

    def test_get_by_deleted(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid, deleted_at=arrow.get())
        save_to_database(t2)

        assert not Table2.get_by('user_uuid', uuid)

    def test_get_by_deleted_contains(self):
        uuid = str(uuid4())
        t2 = Table2(id=1, user_uuid=uuid)
        save_to_database(t2)

        t2 = Table2.get_by('user_uuid', uuid, contains_deleted=True)
        assert t2.id == 1

    def test_get_by_user(self):
        uuid = str(uuid4())
        t21 = Table2(id=1, user_uuid=uuid, key=1, key2=1,
                     created_at=arrow.get('2011-10-21'))
        t22 = Table2(id=2, user_uuid=uuid, key=1, key2=2,
                     created_at=arrow.get('2012-10-21'))
        t23 = Table2(id=3, user_uuid=uuid, key=1, key2=3,
                     created_at=arrow.get('2013-10-21'))
        t24 = Table2(id=4, user_uuid=uuid, key=1, key2=4,
                     created_at=arrow.get('2014-10-21'))
        t25 = Table2(id=5, user_uuid=uuid, key=1, key2=5,
                     created_at=arrow.get('2015-10-21'))
        save_to_database([t21, t22, t23, t24, t25])

        results = Table2.get_by_user(uuid, offset=2, limit=2)
        assert len(results) == 2
        assert results[0].key2 == 3
        assert results[1].key2 == 2
