# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

class TopologicalSorter:
    """
    utility used to generate a topological sorted list

    The goal of this utility is to generate a topological sorted list (using
    depth-first search) based on one or more provided nodes in a prepared graph.
    When ``sort`` is invoked, the sorter will check the graph to leaf nodes and
    visit nodes until a sorted list can be returned. Leaf nodes are determined
    by the provided sorting function ``sort_func`` which will expect a returned
    collection of leaf nodes for an object in  a graph. This sorting method will
    return an order prioritizing leaf nodes instead of parent nodes. The sorter
    can handle being passed multiple nodes in a graph at any time; however, only
    if the graph's structure does not change (i.e. graph edges are not changed).

    Args:
        sort_func: a function to return leaf nodes for a node being
            visited during the sorting process

    Attributes:
        sorted: list of currently sorted objects
    """
    def __init__(self, sort_func):
        assert sort_func, 'no sort function provided'
        self.sorted = []
        self._state = {}
        self._sort_func = sort_func

    def sort(self, obj):
        """
        generate/update a topological sorted list from a object in a graph

        From a provided graph object ``obj``, a topological sorted (depth-first
        search) list will be updated and returned. This sort call can be invoked
        multiple times.

        Args:
            obj: vertex in a graph to sort from

        Returns:
            sorted list of objects; ``None`` if a cyclic graph has been
                detected

            The returned list of objects should not be directly modified until
            all sorting calls (if multiple sort operations a desired) are
            completed.
        """
        if self._visit(obj):
            return self.sorted
        return None

    def reset(self):
        """
        reset the state of the sorter

        Resets tracked state information contained in the sorter and clears the
        known sorted list of vertices.
        """
        self.sorted = []
        self._state = {}

    def _visit(self, obj):
        """
        depth-first search topological sort visit call

        From a provided graph object ``obj``, a topological sorted (depth-first
        search) list will be updated and returned. This sort call can be invoked
        multiple times.

        Args:
            obj: vertex in a graph to sort from

        Returns:
            ``True``, if the sorting was successful; ``False``, if a cyclic
                graph has been detected
        """
        if obj not in self._state:
            self._state[obj] = ''
        if self._state[obj] == 'P':
            return True
        if self._state[obj] == 'T':
            return False
        self._state[obj] = 'T'
        for child in self._sort_func(obj):
            if not self._visit(child):
                return False
        self._state[obj] = 'P'
        self.sorted.append(obj)
        return True
