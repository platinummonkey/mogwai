from __future__ import unicode_literals
from tornado.testing import gen_test

from mogwai._compat import print_
from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel, TestEdgeModel2, TestEdgeModelDouble
from mogwai.exceptions import ValidationError, MogwaiQueryError


@attr('unit', 'edge_io')
class TestEdgeIO(BaseMogwaiTestCase):

    @gen_test
    def test_model_save_and_load(self):
        """
        Tests that models can be saved and retrieved
        """
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            stream = yield v1.outE()
            edges = yield stream.read()
            self.assertEqual(len(edges), 1)
            self.assertEqual(edges[0].id, e1.id)
        finally:
            yield e1.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_model_updating_works_properly(self):
        """
        Tests that subsequent saves after initial model creation work
        """
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            e1.test_val = 20
            yield e1.save()

            stream = yield v1.outE()
            edges = yield stream.read()
            self.assertEqual(len(edges), 1)
            self.assertEqual(edges[0].test_val, 20)
        finally:
            yield e1.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_model_deleting_works_properly(self):
        """
        Tests that an instance's delete method deletes the instance
        """
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            yield e1.delete()
            stream = yield v1.outE()
            edges = yield stream.read()
            self.assertEqual(len(edges), 0)
        finally:
            yield v1.delete()
            yield v2.delete()

        #??????
        # don't actually create a db model and try to delete
        # e2 = TestEdgeModel(v1, v2, test_val=3, name='nonexistant')
        # yield e2.delete()

    @gen_test
    def test_reload(self):
        """
        Tests that the reload method performs an inplace update of an instance's values
        """
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            e2 = yield TestEdgeModel.get(e1.id)
            print_('\n{} {} {}: {} {}'.format(e1.id, e2.id, e1 == e2, e1.test_val, e2.test_val))
            e2.test_val = 5
            yield e2.save()
            print_("{} {} {}: {} {}".format(e1.id, e2.id, e1 == e2, e1.test_val, e2.test_val))

            self.assertEqual(e1.test_val, 3)
            yield e1.reload()
            self.assertEqual(e1.test_val, 5)
            stream = yield v1.outE()
            e1 = yield stream.read()
            e1 = e1[0]
            self.assertEqual(e1.test_val, 5)
        finally:
            yield e1.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_all_method_for_known_ids(self):
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        e2 = yield TestEdgeModel.create(v1, v2, test_val=4)
        try:
            stream = yield TestEdgeModel.all([e1.id, e2.id])
            results = yield stream.read()
            self.assertEqual(len(results), 2)
            for result in results:
                self.assertIsInstance(result, TestEdgeModel)
                self.assertIn(result, [e1, e2])
        finally:
            yield e1.delete()
            yield e2.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_all_method_for_known_bad_input(self):
        from mogwai.exceptions import MogwaiQueryError
        with self.assertRaises(TypeError):
            stream = yield TestEdgeModel.all()
            results = yield stream.read()
        with self.assertRaises(MogwaiQueryError):
            results = yield TestEdgeModel.all(None)
            results = yield stream.read()
        with self.assertRaises(MogwaiQueryError):
            results = yield TestEdgeModel.all('test')
            results = yield stream.read()

    # Need to update client
    # @gen_test
    # def test_all_method_invalid_length(self):
    #     v1 = yield TestVertexModel.create(test_val=8, name='a')
    #     v2 = yield TestVertexModel.create(test_val=7, name='b')
    #     e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
    #     e2 = yield TestEdgeModel.create(v1, v2, test_val=4)
    #     try:
    #         from mogwai.exceptions import MogwaiQueryError
    #         with self.assertRaises(MogwaiQueryError):
    #             stream = yield TestEdgeModel.all([e1.id, e2.id, 'invalid'])
    #             yield stream.read()
    #     finally:
    #         yield e1.delete()
    #         yield e2.delete()
    #         yield v1.delete()
    #         yield v2.delete()

    @gen_test
    def test_in_between_method(self):
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            stream = yield TestEdgeModel.get_between(v1, v2)
            results = yield stream.read()
            self.assertIsInstance(results, list)
            self.assertEqual(results[0], e1)
        finally:
            yield e1.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_validation_error(self):
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        try:
            from mogwai.exceptions import ValidationError
            with self.assertRaises(ValidationError):
                e1 = yield TestEdgeModel.create(v1, None, test_val=3)
            with self.assertRaises(ValidationError):
                e1 = yield TestEdgeModel.create(None, v2, test_val=3)
            with self.assertRaises(ValidationError):
                e1 = yield TestEdgeModel.create(None, None, test_val=3)
        finally:
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_reload_no_changes(self):
        # NOTE titan 0.4.2 and earlier changes made to an edge deletes and then creates a new edge
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=3)
        try:
            yield e1.reload()
        finally:
            yield e1.delete()
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_find_by_value_method(self):
        v1 = yield TestVertexModel.create(test_val=8, name='a')
        v2 = yield TestVertexModel.create(test_val=7, name='b')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=-99, name='e1')
        e2 = yield TestEdgeModel.create(v1, v2, test_val=-100, name='e2')
        e3 = yield TestEdgeModelDouble.create(v1, v2, test_val=-101.0, name='e3')

        try:
            stream = yield TestEdgeModel.find_by_value('test_val', -99)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield TestEdgeModel.find_by_value('test_val', -100)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield TestEdgeModel.find_by_value('test_val', -102)
            results = yield stream.read()
            self.assertEqual(len(results), 0)

            stream = yield TestEdgeModel.find_by_value('name', 'e2')
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield TestEdgeModelDouble.find_by_value('test_val', -101.0)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            print_(e1)
            print_(e2)
            print_(e3)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()

    #
    # def test_get_by_id(self):
    #     e1 = TestEdgeModel.create(v1, v2, test_val=3)
    #     results = TestEdgeModel.get(e1.id)
    #     self.assertIsInstance(results, TestEdgeModel)
    #     self.assertEqual(results, e1)
    #
    #     from mogwai.exceptions import MogwaiQueryError
    #     with self.assertRaises(TestEdgeModel.DoesNotExist):
    #         results = TestEdgeModel.get(None)
    #
    #     with self.assertRaises(TestEdgeModel.DoesNotExist):
    #         results = TestEdgeModel.get('nonexistant')
    #
    #     e2 = TestEdgeModel2.create(v1, v2, test_val=2)
    #     with self.assertRaises(TestEdgeModel.WrongElementType):
    #         results = TestEdgeModel.get(e2.id)
    #
    #     e1.delete()
    #     e2.delete()
    #
    # def test_inV_ouV_vertex_traversal(self):
    #     e1 = TestEdgeModel.create(v1, v2, test_val=3)
    #
    #     v1 = e1.outV()
    #     v2 = e1.inV()
    #     self.assertEqual(v1, v1)
    #     self.assertEqual(v2, v2)
    #
    #     e1.delete()
