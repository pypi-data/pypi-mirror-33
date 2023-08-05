from ucca import convert, layer0, layer1


class DependencyConverter(convert.DependencyConverter):
    """
    Alternative converter to the one in UCCA - instead of introducing UCCA centers etc., create a simple
    hierarchy with "head" edges introduced for each edge head.
    """
    TOP = "TOP"
    HEAD = "head"
    ORPHAN = "orphan"

    def __init__(self, *args, tree=False, punct_tag=None, punct_rel=None, tag_priority=(),
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = tree
        self.punct_tag = punct_tag
        self.punct_rel = punct_rel
        self.lines_read = []
        # noinspection PyTypeChecker
        self.tag_priority = [self.HEAD] + list(tag_priority) + self.TAG_PRIORITY + [None]

    def read_line_and_append(self, read_line, line, *args, **kwargs):
        self.lines_read.append(line)
        try:
            return read_line(line, *args, **kwargs)
        except ValueError as e:
            raise ValueError("Failed reading line:\n" + line) from e

    def split_line(self, line):
        return line.split("\t")

    def create_non_terminals(self, dep_nodes, l1):
        for dep_node in dep_nodes:
            if dep_node.outgoing:
                if not self.tree and dep_node.position and not dep_node.incoming:  # Create top node
                    dep_node.node = dep_node.preterminal = l1.add_fnode(None, (self.ROOT, self.TOP)[dep_node.is_top])
                if self.is_punct(dep_node):  # Avoid outgoing edges from punctuation by flipping edges
                    head = dep_node.incoming[0].head if dep_node.incoming else dep_nodes[0]
                    outgoing = list(dep_node.outgoing)
                    for edge in outgoing:
                        edge.head = head
                    for edge in dep_node.incoming:
                        edge.head = outgoing[0].head
        remote_edges = []
        sorted_dep_nodes = self._topological_sort(dep_nodes)
        self.preprocess(sorted_dep_nodes, to_dep=False)
        for dep_node in sorted_dep_nodes:  # Create all other nodes
            incoming = list(dep_node.incoming)
            if dep_node.is_top and incoming[0].head_index != 0:
                top_edge = self.Edge(head_index=0, rel=self.TOP, remote=False)
                top_edge.head = dep_nodes[0]
                incoming[:0] = [top_edge]
            edge, *remotes = incoming
            self.add_node(dep_node, edge, l1)
            if dep_node.outgoing and not any(map(self.is_flat, dep_node.incoming)):
                dep_node.preterminal = l1.add_fnode(dep_node.preterminal, self.HEAD)  # Intermediate head for hierarchy
            remote_edges += remotes
        for edge in remote_edges:
            parent = edge.head.node or l1.heads[0]
            child = edge.dependent.node or l1.heads[0]
            if child not in parent.children and parent not in child.iter():  # Avoid cycles and multi-edges
                l1.add_remote(parent, edge.rel, child)

    def add_node(self, dep_node, edge, l1):
        # Add top-level edge (like UCCA H) if top-level, otherwise add child to head's node
        dep_node.preterminal = dep_node.node = \
            l1.add_fnode(dep_node.preterminal, self.HEAD) if edge.rel.upper() == self.ROOT else (
                l1.add_fnode(None if self.is_scene(edge) else edge.head.node, edge.rel))

    def from_format(self, lines, passage_id, split=False, return_original=False):
        for passage in super().from_format(lines, passage_id, split=split):
            yield (passage, self.lines_read, passage.ID) if return_original else passage
            self.lines_read = []

    @staticmethod
    def primary_edges(unit, tag=None):
        return (e for e in unit if not e.attrib.get("remote") and not e.child.attrib.get("implicit")
                and (tag is None or e.tag == tag))

    def find_head_child(self, unit):
        try:
            # noinspection PyTypeChecker
            return next(e.child for tag in self.tag_priority for e in self.primary_edges(unit, tag))
        except StopIteration:
            raise RuntimeError("Could not find head child for unit (%s): %s" % (unit.ID, unit))

    def find_head_terminal(self, unit):
        while unit.outgoing:  # still non-terminal
            unit = self.find_head_child(unit)
        if unit.layer.ID != layer0.LAYER_ID:
            raise ValueError("Implicit unit in conversion to dependencies (%s): %s" % (unit.ID, unit.root))
        return unit

    def find_top_headed_edges(self, unit):
        return [e for e in self.find_headed_unit(unit).incoming if e.tag not in (self.ROOT, self.TOP)]

    def preprocess(self, dep_nodes, to_dep=True):
        roots = self.roots(dep_nodes)
        if to_dep and self.tree and len(roots) > 1:
            for root in roots[1:]:
                root.incoming = [e for e in root.incoming if e.rel != self.ROOT.lower() and e.head_index >= 0]
            roots = [roots[0]]
        for dep_node in dep_nodes:
            is_parentless = True
            for edge in dep_node.incoming:
                if edge.remote:
                    if self.is_flat(edge):  # Unanalyzable remote is not possible
                        edge.remove()
                    else:  # Avoid * marking in CoNLL-U
                        edge.remote = False
                else:  # Found primary parent
                    is_parentless = False
            if is_parentless and self.tree:  # Must have exactly one root
                if roots:  # Root already exist, so attach as its child
                    dep_node.incoming = [self.Edge(head_index=roots[0].position - 1, rel=self.ORPHAN, remote=False)]
                else:  # This is the first root
                    roots = [dep_node]
                    dep_node.incoming = [self.Edge(head_index=-1, rel=self.ROOT.lower(), remote=False)]

    def roots(self, dep_nodes):
        return [n for n in dep_nodes if any(e.rel == self.ROOT.lower() for e in n.incoming)]

    def find_headed_unit(self, unit):
        while unit.incoming and (not unit.outgoing or unit.incoming[0].tag == self.HEAD) and \
                not (unit.incoming[0].tag == layer1.EdgeTags.Terminal and unit != unit.parents[0].children[0]):
            unit = unit.parents[0]
        return unit

    def is_top(self, unit):
        return any(e.tag == self.TOP for e in self.find_headed_unit(unit).incoming)

    def is_punct(self, dep_node):
        return dep_node.token and (super().is_punct(dep_node) or dep_node.token.tag == self.punct_tag)

    def is_flat(self, edge):
        return False

    def is_scene(self, edge):
        return False
