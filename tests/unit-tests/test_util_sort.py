# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.sort import TopologicalSorter
from tests import RelengToolTestCase


class TestObj:
    def __init__(self, name):
        self.children = []
        self.name = name

    def __repr__(self):
        return self.name


class TestUtilSort(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        def sorting_method(obj):
            return obj.children
        cls.sorter = TopologicalSorter(sorting_method)

    def test_utilsort_topologicalsorter_simple(self):
        """
        simple sorting tests
        """
        # a -> b -> c -> d -> e
        a = TestObj('a')
        b = TestObj('b')
        c = TestObj('c')
        d = TestObj('d')
        e = TestObj('e')
        a.children.append(b)
        b.children.append(c)
        c.children.append(d)
        d.children.append(e)

        sorted_ = self.sorter.sort(e)
        self.assertEqual(sorted_, [e])
        self.sorter.reset()

        sorted_ = self.sorter.sort(c)
        self.assertEqual(sorted_, [e, d, c])
        self.sorter.reset()

        sorted_ = self.sorter.sort(a)
        self.assertEqual(sorted_, [e, d, c, b, a])
        self.sorter.reset()

        self.sorter.sort(e)
        self.sorter.sort(b)
        self.sorter.sort(c)
        self.sorter.sort(d)
        sorted_ = self.sorter.sort(e)
        self.assertEqual(sorted_, [e, d, c, b])

    def test_utilsort_topologicalsorter_ordering(self):
        """
        ensure the order objects are provided matters (i.e. user priority)
        """
        # a, b, c
        a = TestObj('a')
        b = TestObj('b')
        c = TestObj('c')

        self.sorter.sort(a)
        self.sorter.sort(b)
        sorted_ = self.sorter.sort(c)
        self.assertEqual(sorted_, [a, b, c])
        self.sorter.reset()

        self.sorter.sort(b)
        self.sorter.sort(a)
        sorted_ = self.sorter.sort(c)
        self.assertEqual(sorted_, [b, a, c])
        self.sorter.reset()

        self.sorter.sort(c)
        self.sorter.sort(a)
        sorted_ = self.sorter.sort(b)
        self.assertEqual(sorted_, [c, a, b])
        self.sorter.reset()

        self.sorter.sort(c)
        self.sorter.sort(b)
        sorted_ = self.sorter.sort(a)
        self.assertEqual(sorted_, [c, b, a])

    def test_utilsort_topologicalsorter_multiple(self):
        """
        a bit less simple sorting test
        """
        #  /-> b
        # a
        #  \-> c -> d -> e, f, g
        a = TestObj('a')
        b = TestObj('b')
        c = TestObj('c')
        d = TestObj('d')
        e = TestObj('e')
        f = TestObj('f')
        g = TestObj('g')
        a.children.append(b)
        a.children.append(c)
        c.children.append(d)
        d.children.append(e)
        d.children.append(f)
        d.children.append(g)

        sorted_ = self.sorter.sort(a)
        self.assertEqual(sorted_, [b, e, f, g, d, c, a])

    def test_utilsort_topologicalsorter_complex(self):
        """
        complex sorting test
        """
        # a      -> f -> g
        #       /    \
        # b -> e      -> h -------------------> r
        #            /                      /
        # c -> i -> j -> x -> m, n, o, p   /
        #  /                              /
        # d ------> k -----------------> q
        #
        a = TestObj('a')
        b = TestObj('b')
        c = TestObj('c')
        d = TestObj('d')
        e = TestObj('e')
        f = TestObj('f')
        g = TestObj('g')
        h = TestObj('h')
        i = TestObj('i')
        j = TestObj('j')
        k = TestObj('k')
        x = TestObj('x')
        m = TestObj('m')
        n = TestObj('n')
        o = TestObj('o')
        p = TestObj('p')
        q = TestObj('q')
        r = TestObj('r')
        b.children.append(e)
        c.children.append(i)
        d.children.extend([i, k])
        e.children.append(f)
        f.children.extend([g, h])
        h.children.append(r)
        i.children.append(j)
        j.children.extend([h, x])
        k.children.append(q)
        x.children.extend([m, n, o, p])
        q.children.append(r)

        self.sorter.sort(a)
        self.sorter.sort(b)
        self.sorter.sort(c)
        self.sorter.sort(d)
        self.assertEqual(self.sorter.sorted,
            [a, g, r, h, f, e, b, m, n, o, p, x, j, i, c, q, k, d])

    def tearDown(self):
        self.sorter.reset()
