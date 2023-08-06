# pylint: disable=invalid-name,too-many-public-methods
import asyncio
from datetime import timedelta
import time
import threading
import unittest

import asynctest
from toolz.itertoolz import count

from anji_orm import orm_register

from .models import T1


class SyncTestSkeleton(unittest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstrac class")
        orm_register.init(connection_uri, pool_kwargs)

    def setUp(self):
        orm_register.load()

    def tearDown(self):
        orm_register.sync_strategy.drop_table(T1._table)

    @classmethod
    def tearDownClass(cls):
        orm_register.close()

    def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        t1.send()
        t2.send()
        t1_list = T1.all().run()
        self.assertEqual(count(t1_list), 2)

    def test_simple_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = list((T1.c1 > '5').run())
        self.assertEqual(count(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        t1_1.send()
        t1_2 = next(T1.all().run())
        t1_2.c2 = '7'
        t1_2.send()
        t1_1.load()
        self.assertEqual(t1_1.c2, '7')

    def test_datetime(self):
        test_datetime = orm_register.current_utc_datetime() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        t1_original.send()
        t1_1 = next(T1.all().run())
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = next((T1.c3 == test_datetime).run())
        self.assertEqual(t1_2.c3, t1_original.c3)

    def test_complex_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = list(((T1.c1 > '5') & (T1.c1 < '8')).run())
        self.assertEqual(count(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_sorting(self):
        for c1 in map(str, range(0, 3)):
            for c2 in map(str, range(0, 3)):
                T1(c1=c1, c2=c2).send()
        t1_list = T1.all().order_by(T1.c1.amount.desc, T1.c2.amount.desc).run()
        t1_first = next(t1_list)
        self.assertEqual(t1_first.c1, '2')
        self.assertEqual(t1_first.c2, '2')

    def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        t1.send()
        t1_search = next((T1.c4.c2 == 5).run())
        self.assertEqual(t1.c4, t1_search.c4)

    def test_complex_nested_queries(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        t1_list = ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).run()
        self.assertEqual(count(t1_list), 6)

    def test_internval_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).run()
        self.assertEqual(count(t1_list), 2)

    def test_in_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = (T1.c4.c1.one_of(1, 2)).run()
        self.assertEqual(count(t1_list), 2)

    def test_sample(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = T1.all().sample(2).run()
        self.assertEqual(count(t1_list), 2)

    def test_base_aggregation(self):
        for c1 in range(0, 5):
            T1(c1='v' + str(c1)).send()
        self.assertEqual(T1.all().max(T1.c1).run(), 'v4')

    def test_nested_aggregation(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        self.assertEqual(T1.all().max(T1.c4.c1).run(), 4)

    def test_complicated_aggregation(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        self.assertEqual((T1.c4.c1 > T1.c4.c2).count().run(), 10)

    def test_complicated_query(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        self.assertEqual(count((T1.c4.c1 > T1.c4.c2).run()), 10)

    def test_base_match(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}").send()
        self.assertEqual(count(T1.c5.match('v0').run()), 5)

    def test_match_aggregation(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}").send()
        self.assertEqual(T1.c5.match('v0').count().run(), 5)

    def test_match_complicated(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}", c1=str(c1), c2=str(c2)).send()
        self.assertEqual((T1.c5.match('v0') & (T1.c1 != T1.c2)).count().run(), 4)

    def test_group(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c1=str(c1), c2=str(c2)).send()
        self.assertEqual(T1.c1.ne(T1.c2).group(T1.c2).count().run(), {'0': 4, '1': 4})

    def test_changes(self):
        event_list = []

        def changes_sender(t1_list):
            time.sleep(2)
            for t1 in t1_list:
                t1.c1 = '2'
                t1.send()
            time.sleep(2)

        def changes_aggregator():
            for event in T1.c2.eq('1').changes(with_types=True).run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2=str(c2))
            for c1 in range(0, 5) for c2 in range(0, 2)
        ]
        for t1 in t1_list:
            t1.send()
        additional_thread = threading.Thread(target=changes_aggregator, daemon=True)
        additional_thread.start()
        changes_sender(t1_list)
        self.assertEqual(len(event_list), 5)
        for event in event_list:
            self.assertEqual(event.get('type'), 'change')
            self.assertTrue('doc' in event)

    def test_complex_changes(self):
        event_list = []

        def changes_sender(t1_list):
            time.sleep(5)
            for t1 in t1_list:
                t1.c1 = '-'
                t1.send()
            time.sleep(5)

        def changes_aggregator():
            for event in T1.c1.le(T1.c2).changes(with_types=True, with_initial=True).run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2='3')
            for c1 in range(0, 5)
        ]
        for t1 in t1_list:
            t1.send()
        additional_thread = threading.Thread(target=changes_aggregator, daemon=True)
        additional_thread.start()
        changes_sender(t1_list)
        self.assertEqual(len(event_list), 9)
        for event in event_list:
            self.assertIn(event.get('type'), ('change', 'add', 'initial'))
            self.assertTrue('doc' in event)

    def test_update(self):
        for c1 in range(0, 5):
            T1(c1=str(c1), c2='5').send()
        update_result = T1.c2.eq('5').update({'c2': '6'}).run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', T1.all().run())
        ))

    def test_atomic_update(self):
        for c1 in range(0, 5):
            T1(c1=str(c1), c2='5').send()
        update_result = T1.c2.eq('5').update({'c2': '6'}, atomic=True).run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', T1.all().run())
        ))


class AsyncTestSkeleton(asynctest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstrac class")
        orm_register.init(connection_uri, pool_kwargs, async_mode=True)

    async def setUp(self):
        await orm_register.async_load()

    async def tearDown(self):
        await orm_register.async_strategy.drop_table(T1._table)

    @classmethod
    def tearDownClass(cls):
        asyncio.get_event_loop().run_until_complete(orm_register.async_close())

    async def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        await asyncio.gather(t1.async_send(), t2.async_send())
        t1_list = await T1.all().async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_simple_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = list(await (T1.c1 > '5').async_run())
        self.assertEqual(count(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        await t1_1.async_send()
        t1_2 = next(await T1.all().async_run())
        t1_2.c2 = '7'
        await t1_2.async_send()
        await t1_1.async_load()
        self.assertEqual(t1_1.c2, '7')

    async def test_datetime(self):
        test_datetime = orm_register.current_utc_datetime() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        await t1_original.async_send()
        t1_1 = next(await T1.all().async_run())
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = next(await (T1.c3 == test_datetime).async_run())
        self.assertEqual(t1_2.c3, t1_original.c3)

    async def test_complex_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = list(await ((T1.c1 > '5') & (T1.c1 < '8')).async_run())
        self.assertEqual(count(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_sorting(self):
        await asyncio.wait([
            T1(c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 3) for c2 in range(0, 3)
        ])
        t1_list = await T1.all().order_by(T1.c1.amount.desc, T1.c2.amount.desc).async_run()
        t1_el = next(t1_list)
        self.assertEqual(t1_el.c1, '2')
        self.assertEqual(t1_el.c2, '2')

    async def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        await t1.async_send()
        t1_search = next(await (T1.c4.c2 == 5).async_run())
        self.assertEqual(t1.c4, t1_search.c4)

    async def test_complex_nested_queries(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        t1_list = await ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).async_run()
        self.assertEqual(count(t1_list), 6)

    async def test_internval_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_in_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await (T1.c4.c1.one_of(1, 2)).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_sample(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await T1.all().sample(2).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_base_aggregation(self):
        await asyncio.wait([T1(c1='v' + str(c1)).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c1).async_run(), 'v4')

    async def test_nested_aggregation(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c4.c1).async_run(), 4)

    async def test_complicated_aggregation(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        self.assertEqual(await (T1.c4.c1 > T1.c4.c2).count().async_run(), 10)

    async def test_complicated_query(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        self.assertEqual(count(await (T1.c4.c1 > T1.c4.c2).async_run()), 10)

    async def test_base_match(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}").async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(count(await T1.c5.match('v0').async_run()), 5)

    async def test_match_aggregation(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}").async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await T1.c5.match('v0').count().async_run(), 5)

    async def test_match_complicated(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}", c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await (T1.c5.match('v0') & (T1.c1 != T1.c2)).count().async_run(), 4)

    async def test_group(self):
        await asyncio.wait([
            T1(c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await T1.c1.ne(T1.c2).group(T1.c2).count().async_run(), {'0': 4, '1': 4})

    async def test_changes(self):
        event_list = []

        async def changes_sender(t1_list):
            await asyncio.sleep(2)
            for t1 in t1_list:
                t1.c1 = '2'
                await t1.async_send()
            await asyncio.sleep(2)

        async def changes_aggregator():
            async for event in await T1.c2.eq('1').changes(with_types=True).async_run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2=str(c2))
            for c1 in range(0, 5) for c2 in range(0, 2)
        ]
        await asyncio.wait([t1.async_send() for t1 in t1_list])
        await asyncio.wait([
            changes_sender(t1_list),
            changes_aggregator()
        ], return_when=asyncio.FIRST_COMPLETED)
        self.assertEqual(len(event_list), 5)
        for event in event_list:
            self.assertEqual(event.get('type'), 'change')
            self.assertTrue('doc' in event)

    async def test_complex_changes(self):
        event_list = []

        async def changes_sender(t1_list):
            await asyncio.sleep(2)
            for t1 in t1_list:
                t1.c1 = '-'
                await t1.async_send()
            await asyncio.sleep(2)

        async def changes_aggregator():
            async for event in await T1.c1.le(T1.c2).changes(with_types=True, with_initial=True).async_run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2='3')
            for c1 in range(0, 5)
        ]
        await asyncio.wait([t1.async_send() for t1 in t1_list])
        await asyncio.wait([
            changes_sender(t1_list),
            changes_aggregator()
        ], return_when=asyncio.FIRST_COMPLETED)
        self.assertEqual(len(event_list), 9)
        for event in event_list:
            self.assertIn(event.get('type'), ('change', 'add', 'initial'))
            self.assertTrue('doc' in event)

    async def test_update(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 5)])
        update_result = await T1.c2.eq('5').update({'c2': '6'}).async_run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', await T1.all().async_run())
        ))

    async def test_atomic_update(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 5)])
        update_result = await T1.c2.eq('5').update({'c2': '6'}, atomic=True).async_run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', await T1.all().async_run())
        ))
