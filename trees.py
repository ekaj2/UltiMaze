IN_BLENDER = False

import logging

if IN_BLENDER:
    from maze_gen.logging_setup import setup_logger
else:
    from logging_setup import setup_logger


class RebelChildError(Exception):
    def __init__(self, nodes, parent, child):
        self.nodes = nodes
        self.parent = parent
        self.child = child

    def __str__(self):
        return repr(self)

    def __repr__(self):
        ret = "\n"
        ret += str(self.parent) + ": " + str(self.nodes[self.parent]) + "\n"
        ret += str(self.child) + ": " + str(self.nodes[self.child])
        return ret


class LoopInTreeError(Exception):
    def __init__(self, nodes, looping):
        self.nodes = nodes
        self.looping = looping

    def __str__(self):

        ret = "\n\n" + "+" * 50 + "\n\n"
        ret += "Nodes:\n\n" + "\n".join([str(self.nodes[a]) for a in self.nodes])
        ret += "\n\nLooping Nodes:\n\n" + str(self.looping)
        ret += "\n\n" + "-" * 50 + "\n\n"

        return ret

    def __repr__(self):
        ret = "\n" + str(self.nodes) + "\n\n" + str(self.looping) + "\n"
        return ret


class Tree:
    setup_logger(__name__)

    def __init__(self):
        self.nodes = {}

    def __str__(self):
        ret = ""
        for lvl in range(self.num_levels()):
            lvl_names = self.get_level(lvl)
            for name in lvl_names:
                ret += str(name) + ", "
            ret += "\n"
        return ret

    def __repr__(self):
        ret = ""
        for node in self.nodes:
            ret += str(node) + ": " + str(self.nodes[node]) + "\n"
        return ret

    def check_for_bad_dependencies(self):
        def check_for_rebellious_child():
            # check for when a node's child doesn't recognize it as a parent
            for node in self.get_nodes():
                for child in self.nodes[node]['children']:
                    if self.nodes[child]['parent'] != node:
                        raise RebelChildError(self.nodes, node, child)

        def check_for_loops():
            # check for when a node is parented to it's parent
            for node in self.get_nodes():
                nodes_parent = self.nodes[node]['parent']
                nodes = [node]
                while nodes_parent is not None:
                    nodes += [nodes_parent]
                    if self.nodes[nodes_parent]['parent'] == node:
                        raise LoopInTreeError(self.nodes, nodes)
                    nodes_parent = self.nodes[nodes_parent]['parent']

        check_for_rebellious_child()
        check_for_loops()

    def new_node(self, name='root', parent=None):
        """Adds a new node to the tree."""

        # create a new key/value for the node
        self.nodes[name] = {'parent': parent, 'children': set()}
        if parent is not None:
            self.parent(name, parent)

    def delete_node(self, node):
        this_node = self.nodes[node]

        # remove from parent's children list
        self.nodes[this_node['parent']]['children'].remove(node)

        # set all children as roots
        for child in this_node['children']:
            self.nodes[child]['parent'] = None

        # delete node
        del this_node

    def child_of(self, child, parent):
        """Returns True of child is a child of parent, False otherwise."""
        node = child
        while True:
            node = self.nodes[node]['parent']
            if node == parent:
                return True
            elif node is None:
                return False

    def parent(self, child, parent):
        # fix for 'looping' parents
        if self.nodes[parent]['parent'] == child:
            self.nodes[parent]['parent'] = None
        self.nodes[parent]['children'].add(child)
        self.nodes[child]['parent'] = parent

    def unparent(self, child):
        parent = self.nodes[child]['parent']
        if parent is not None:
            self.nodes[parent]['children'].remove(child)
            self.nodes[child]['parent'] = None
        else:
            logger = logging.getLogger(__name__)
            logger.warning("Node {} is a root! Cannot unparent root!".format(child))

    def insert_parent(self, parent, child):
        print("Only a stub")

    def child_shift_detach(self, node):
        parent = self.nodes[node]['parent']

        # attach children to parent
        for c in self.nodes[node]['children']:
            if parent is not None:
                self.nodes[parent]['children'].add(c)
            self.nodes[c]['parent'] = parent

        self.nodes[node]['children'].clear()

        # remove from parent's children list and set as root
        if parent is not None:
            self.nodes[parent]['children'].remove(node)
            self.nodes[node]['parent'] = None
        else:
            logger = logging.getLogger(__name__)
            logger.info("Node {} is a root already".format(node))

    def replacement_child_shift_detach(self, node):
        children = self.nodes[node]['children']
        if children:

            # unparent the first child...must be done differently b/c of pop()
            first_child = children.pop()
            self.nodes[first_child]['parent'] = None

            # if the node that is being detached has a parent...parent the first child to that parent
            if self.nodes[node]['parent'] is not None:
                self.unparent(first_child)  # todo - figure out if this is needed
                self.parent(first_child, self.nodes[node]['parent'])

            # for rest of the children: unparent them from the detachee then parent to first child
            # the children need to be copied to a list b/c the set doesn't support the children count changing
            for child in list(children):
                self.unparent(child)
                self.parent(child, first_child)
        # detach node (should have no children now)
        self.unparent(node)

    def prune_leaves(self, iterations):
        for i in range(iterations):
            leaves = self.get_leaves()
            for leaf_node in leaves:
                parent = self.nodes[leaf_node]['parent']
                try:
                    self.nodes[parent]['children'].remove(leaf_node)
                except KeyError:
                    print("Removing root from its parent's children list failed: roots don't have parents!")
                del self.nodes[leaf_node]

    def prune_roots(self, iterations):
        for i in range(iterations):
            roots = self.get_roots()
            for root_node in roots:
                children = self.nodes[root_node]['children']
                for child in children:
                    self.nodes[child]['parent'] = None
                del self.nodes[root_node]

    def num_levels(self):
        old_lvl_nodes = self.get_roots()
        # the '[] + ' is to keep it from referencing the same value in memory
        curr_lvl_nodes = [] + old_lvl_nodes
        lvls = 0
        while curr_lvl_nodes:
            curr_lvl_nodes = []
            for node in old_lvl_nodes:
                for child in self.nodes[node]['children']:
                    curr_lvl_nodes += [child]
            old_lvl_nodes = curr_lvl_nodes
            lvls += 1
        return lvls

    def get_level(self, lvl):
        """Returns [nodes] at lvl where lvl = 0 returns roots."""
        old_lvl_nodes = self.get_roots()
        # the '[] + ' is to keep it from referencing the same value in memory
        curr_lvl_nodes = [] + old_lvl_nodes
        for i in range(lvl):
            curr_lvl_nodes = []
            for node in old_lvl_nodes:
                for child in self.nodes[node]['children']:
                    curr_lvl_nodes += [child]
            old_lvl_nodes = curr_lvl_nodes
        return curr_lvl_nodes

    def get_root(self, child):
        node = child
        while True:
            if self.nodes[node]['parent'] is None:
                return node
            node = self.nodes[node]['parent']

    def get_nodes(self):
        return [a for a in self.nodes]

    def get_leaves(self):
        return [a for a in self.nodes if not self.nodes[a]['children']]

    def get_roots(self):
        return [a for a in self.nodes if self.nodes[a]['parent'] is None]

    def clear(self):
        self.nodes = {}

    def unparent_children(self, parent):
        # set all children as roots
        for child in self.nodes[parent]['children']:
            self.nodes[child]['parent'] = None

        # remove from parent's children list
        self.nodes[parent]['children'] = set()


def main():
    tree = Tree()
    tree.new_node(name='root')
    tree.new_node(name='trunk', parent='root')
    for i in range(3):
        tree.new_node(name='branch' + str(i+1), parent='trunk')

    print(tree.child_of('branch1', 'root'))
    tree.unparent('branch1')
    print(tree.get_roots())
    print(tree.get_leaves())
    print(tree.get_nodes())
    tree.parent('branch1', 'branch2')
    print(tree.child_of('branch1', 'branch3'))
    print(tree.get_root('branch1'))

    print(tree)

    print("\n" + "*" * 25 + "\n")

    tree.prune_leaves(0)
    print(tree)

    tree.delete_node('branch2')
    print(tree.get_level(0))
    print(tree)

if __name__ == "__main__":
    main()
