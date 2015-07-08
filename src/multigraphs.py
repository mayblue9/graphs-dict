#!/usr/bin/python

class MultiGraph(dict):
    """The class defining a weighted multigraph."""

    def __init__(self, n=0, directed=False):
        """Loads up a MultiGraph instance."""
        self.n = n              # compatibility
        self.directed = directed  # bool

    def v(self):
        """Returns the number of nodes (the multigraph order)."""
        return len(self)

    def e(self):
        """Returns the number of edges."""
        loops = 0
        for node in self:
            if node in self[node]:
                loops = loops + len(self[node][node])
        edges = 0
        for source in self:
            for target in self[source]:
                edges = edges + len(self[source][target])
        if self.is_directed():
            return edges
        else:
            return (edges + loops) / 2

    def is_directed(self):
        """Test if the multigraph is directed."""
        return self.directed

    def add_node(self, node):
        """Add a node to the multigraph."""
        if node not in self:
            self[node] = dict()

    def has_node(self, node):
        """Test if a node exists."""
        return node in self

    def del_node(self, node):
        """Remove a node from the multigraph (with edges)."""
        # The dictionary changes size during iteration.
        for edge in list(self.iterinedges(node)):
            self.del_edge(edge)
        if self.is_directed():
            for edge in list(self.iteroutedges(node)):
                self.del_edge(edge)
        del self[node]

    def add_edge(self, edge):
        """Add an edge to the multigraph (missing nodes are created)."""
        self.add_node(edge.source)
        self.add_node(edge.target)
        if edge.target not in self[edge.source]:
            self[edge.source][edge.target] = list()
        if not self.is_directed() and edge.source not in self[edge.target]:
            self[edge.target][edge.source] = list()
        # Increase the number of parallel edges.
        self[edge.source][edge.target].append(edge)
        # A loop is added only once.
        if not self.is_directed() and edge.source != edge.target:
            self[edge.target][edge.source].append(~edge)

    def del_edge(self, edge):
        """Remove an edge from the multigraph."""
        self[edge.source][edge.target].remove(edge)
        if len(self[edge.source][edge.target]) == 0:
            del self[edge.source][edge.target]
        # A loop is deleted only once.
        if not self.is_directed() and edge.source != edge.target:
            self[edge.target][edge.source].remove(~edge)
            if len(self[edge.target][edge.source]) == 0:
                del self[edge.target][edge.source]

    def has_edge(self, edge):
        """Test if an edge exists. The weight is not checked."""
        return edge.source in self and edge.target in self[edge.source]

    def weight(self, edge):
        """Return the number of parallel edges."""
        if edge.source in self and edge.target in self[edge.source]:
            return len(self[edge.source][edge.target])
        else:
            return 0

    def iternodes(self):
        """Generates nodes from the multigraph on demand."""
        return self.iterkeys()

    def iteradjacent(self, source):
        """Generates adjacent nodes from the multigraph on demand."""
        return self[source].iterkeys()

    def iteroutedges(self, source):
        """Generates outedges from the multigraph on demand."""
        for target in self[source]:
            for edge in self[source][target]:
                yield edge

    def iterinedges(self, source):
        """Generates inedges from the multigraph on demand."""
        if self.is_directed():
            for target in self.iternodes():
                if source in self[target]:
                    for edge in self[target][source]:
                        yield edge
        else:
            for target in self[source]:
                for edge in self[source][target]:
                    yield ~edge   # inverted

    def iteredges(self):
        """Generates edges from the multigraph on demand."""
        for source in self.iternodes():
            for target in self[source]:
                # source <= target, because loops are possible.
                if self.is_directed() or source <= target:
                    for edge in self[source][target]:
                        yield edge

    def show(self):
        """The multigraph presentation."""
        for source in self.iternodes():
            print source, ":",
            for target in self[source]:
                print "%s(%s)" % (target, len(self[source][target])),
            print

    def copy(self):
        """Return the multigraph copy."""
        new_graph = MultiGraph(n=self.n, directed=self.directed)
        for source in self.iternodes():
            new_graph[source] = dict()
            for target in self[source]:
                new_graph[source][target] = list(self[source][target])
        return new_graph

    def transpose(self):
        """Return the transpose of the multigraph."""
        new_graph = MultiGraph(n=self.n, directed=self.directed)
        for node in self.iternodes():
            new_graph.add_node(node)
        for edge in self.iteredges():
            new_graph.add_edge(~edge)
        return new_graph

    def degree(self, source):
        """Return the degree of the node in the undirected graph."""
        if self.is_directed():
            raise ValueError("the graph is directed")
        if source in self[source]:
            loops = len(self[source][source])
        else:
            loops = 0
        edges = 0
        for target in self[source]:
            edges = edges + len(self[source][target])
        return edges + loops

    def outdegree(self, source):
        """Return the outdegree of the node."""
        if source in self[source]:
            loops = len(self[source][source])
        else:
            loops = 0
        edges = 0
        for target in self[source]:
            edges = edges + len(self[source][target])
        if self.is_directed():
            return edges
        else:   # degree
            return edges + loops

    def indegree(self, source):
        """Return the indegree of the node."""
        if self.is_directed():
            edges = 0
            for target in self.iternodes():
                if source in self[target]:
                    edges = edges + len(self[target][source])
            return edges
        else:   # degree
            if source in self[source]:
                loops = len(self[source][source])
            else:
                loops = 0
            edges = 0
            for target in self[source]:
                edges = edges + len(self[source][target])
            return edges + loops

    def __eq__(self, other):   # FIX
        """Test if the multigraphs are equal."""
        if self.is_directed() is not other.is_directed():
            #print "directed and undirected multigraphs"
            return False
        if self.v() != other.v():
            #print "|V1| != |V2|"
            return False
        for node in self.iternodes():   # time O(V)
            if not other.has_node(node):
                #print "V1 != V2"
                return False
        if self.e() != other.e():   # inefficient, time O(E)
            #print "|E1| != |E2|"
            return False
        for edge in self.iteredges():   # time O(E)
            if not other.has_edge(edge):
                #print "E1 != E2"
                return False
        return True

    def __ne__(self, other):
        """Test if the multigraphs are not equal."""
        return not self == other

    def add_multigraph(self, other):
        """Add a multigraph to this multigraph (the current multigraph is modified)."""
        for node in other.iternodes():
            self.add_node(node)
        for edge in other.iteredges():
            self.add_edge(edge)

# EOF
