# Copyright 2017 Integrity Software and Games, LLC
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of UltiMaze.
#
# UltiMaze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltiMaze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltiMaze.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import unittest

from trees import LoopInTreeError, RebelChildError
from trees import Tree


def add_adam_nodes(tree):
    # generation 1
    tree.new_node("Adam")
    # generation 2
    tree.new_node("Cain", "Adam")
    tree.new_node("Abel", "Adam")
    tree.new_node("Seth", "Adam")
    # generation 3
    tree.new_node("Enoch", "Cain")

    return tree


def add_shem_nodes(tree):
    # generation 1
    tree.new_node("Shem")

    # generation 2
    tree.new_node("Arphaxad", "Shem")
    tree.new_node("Lud", "Shem")
    tree.new_node("Aram", "Shem")
    tree.new_node("Asshur", "Shem")
    tree.new_node("Elam", "Shem")

    # generation 3

    # Aram's Kids
    tree.new_node("Uz", "Aram")
    tree.new_node("Hul", "Aram")
    tree.new_node("Mash", "Aram")
    tree.new_node("Gether", "Aram")

    # Arphaxad's kids
    tree.new_node("Salah", "Arphaxad")

    # generation 4
    tree.new_node("Eber", "Salah")

    # generation 5
    tree.new_node("Peleg", "Eber")
    tree.new_node("Joktan", "Eber")

    return tree


class TestNewNode(unittest.TestCase):
    maxDiff = 10000

    def test_simple_addition(self):
        tree = Tree()
        tree.new_node("Adam")
        tree.new_node("Abel", "Adam")
        tree.new_node("Seth", "Adam")
        tree.new_node("Enos", "Seth")
        self.assertEqual(tree.nodes, {"Adam": {'children': set(["Abel", "Seth"]), 'parent': None},
                                      "Abel": {'children': set(), 'parent': "Adam"},
                                      "Seth": {'children': set(["Enos"]), 'parent': "Adam"},
                                      "Enos": {'children': set(), 'parent': "Seth"}})

    def test_three_generation_addition(self):
        tree = Tree()
        # generation 1
        tree.new_node("Adam")
        # generation 2
        tree.new_node("Cain", "Adam")
        tree.new_node("Abel", "Adam")
        tree.new_node("Seth", "Adam")
        # generation 3
        tree.new_node("Enoch", "Cain")

        self.assertEqual(tree.nodes,
                         {"Adam": {'children': set(["Cain", "Abel", "Seth"]), 'parent': None},
                          "Cain": {'children': set(["Enoch"]), 'parent': "Adam"},
                          "Abel": {'children': set(), 'parent': "Adam"},
                          "Seth": {'children': set(), 'parent': "Adam"},
                          "Enoch": {'children': set(), 'parent': "Cain"}})

    def test_add_shem_nodes(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Arphaxad", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(["Salah"]), 'parent': "Shem"},
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Arphaxad"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })


class TestParenting(unittest.TestCase):
    maxDiff = 10000

    def test_unparent_leaf_child(self):
        tree = Tree()
        tree = add_adam_nodes(tree)

        tree.unparent("Enoch")

        self.assertEqual(tree.nodes,
                         {"Adam": {'children': set(["Cain", "Abel", "Seth"]), 'parent': None},
                          "Cain": {'children': set(), 'parent': "Adam"},
                          "Abel": {'children': set(), 'parent': "Adam"},
                          "Seth": {'children': set(), 'parent': "Adam"},
                          "Enoch": {'children': set(), 'parent': None}})

    def test_unparent_arphaxad(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.unparent("Arphaxad")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(["Salah"]), 'parent': None},  # Arphaxad has no parent...
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Arphaxad"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

    def test_parent_reu_to_peleg(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.new_node("Reu")
        tree.parent("Reu", "Peleg")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Arphaxad", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(["Salah"]), 'parent': "Shem"},
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Arphaxad"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(["Reu"]), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"},
                          # Peleg's Son Reu
                          "Reu": {'children': set(), 'parent': "Peleg"}
                          })

    def test_unparent_shems_children(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.unparent_children("Shem")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': None},
                          "Elam": {'children': set(), 'parent': None},
                          "Asshur": {'children': set(), 'parent': None},
                          "Arphaxad": {'children': set(["Salah"]), 'parent': None},
                          "Lud": {'children': set(), 'parent': None},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Arphaxad"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

    def test_unparent_arphaxads_children(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.unparent_children("Arphaxad")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Arphaxad", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(), 'parent': "Shem"},
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': None},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

    def test_bad_parent_reference(self):
        tree = Tree()
        with self.assertRaises(KeyError):
            tree.new_node("Joe", "Bob")


class TestDetaching(unittest.TestCase):
    maxDiff = 10000

    def test_detach_salah(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.replacement_child_shift_detach("Salah")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Arphaxad", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(["Eber"]), 'parent': "Shem"},
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(), 'parent': None},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Arphaxad"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

        tree.check_for_bad_dependencies()

    def test_detach_multiple(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.replacement_child_shift_detach("Salah")
        tree.replacement_child_shift_detach("Salah")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Arphaxad", "Lud"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(["Eber"]), 'parent': "Shem"},
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(), 'parent': None},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Arphaxad"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

        tree.check_for_bad_dependencies()

    def test_shift_detach_arphaxad(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.child_shift_detach("Arphaxad")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Lud", "Salah"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(), 'parent': None},  # Arphaxad is detached (no kids or parents)
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Shem"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

        tree.check_for_bad_dependencies()

    def test_replacement_shift_detach_with_one_child(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.replacement_child_shift_detach("Arphaxad")

        self.assertEqual(tree.nodes,
                         {"Shem": {'children': set(["Aram", "Elam", "Asshur", "Lud", "Salah"]), 'parent': None},
                          # Shem's Kids
                          "Aram": {'children': set(["Uz", "Hul", "Mash", "Gether"]), 'parent': "Shem"},
                          "Elam": {'children': set(), 'parent': "Shem"},
                          "Asshur": {'children': set(), 'parent': "Shem"},
                          "Arphaxad": {'children': set(), 'parent': None},  # Arphaxad is detached (no kids or parents)
                          "Lud": {'children': set(), 'parent': "Shem"},
                          # Aram's Kids
                          "Uz": {'children': set(), 'parent': "Aram"},
                          "Hul": {'children': set(), 'parent': "Aram"},
                          "Mash": {'children': set(), 'parent': "Aram"},
                          "Gether": {'children': set(), 'parent': "Aram"},
                          # Arphaxad's Lineage
                          "Salah": {'children': set(["Eber"]), 'parent': "Shem"},
                          "Eber": {'children': set(["Peleg", "Joktan"]), 'parent': "Salah"},
                          "Peleg": {'children': set(), 'parent': "Eber"},
                          "Joktan": {'children': set(), 'parent': "Eber"}
                          })

        tree.check_for_bad_dependencies()

    def test_replacement_shift_detach_with_two_children(self):
        """Tests for detaching Eber from Shem's family tree.

        This is harder to test b/c it is essentially random because the children are stored in a set,
        and Peleg OR Joktan can be chosen.
        """
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.replacement_child_shift_detach("Eber")
        ebers_kids = ["Peleg", "Joktan"]

        for salah_kid in tree.nodes["Salah"]['children']:
            break
        self.assertIn(salah_kid, ebers_kids)

        self.assertEqual(set(tree.get_roots()), set(["Shem", "Eber"]))

        leaves = tree.get_leaves()
        names = ["Uz", "Hul", "Mash", "Gether", "Lud", "Asshur", "Elam", "Eber"]  # Eber is a node, root, AND leaf
        self.assertEqual(len(names) + 1, len(leaves))
        for name in names:
            self.assertIn(name, leaves)
            leaves.remove(name)
        self.assertEqual(1, len(leaves))
        self.assertIn(leaves[0], ["Peleg", "Joktan"])

        tree.check_for_bad_dependencies()

    def test_reparenting_bug(self):
        """This is the result of a nasty bug that caused looping:
        when this would happen b/c 2 would not be unparented from 1 :(

        Update: actually it doesn't seem to be catching that bug :|
            this thing is SO elusive

        0       1  0
        |       | /
        1   ->  2
        |
        2

        """
        tree = Tree()
        tree.new_node(0)
        tree.new_node(1, 0)
        tree.new_node(2, 1)
        tree.replacement_child_shift_detach(1)
        self.assertEqual(tree.nodes[1]['children'], set())
        self.assertEqual(tree.nodes[2]['parent'], 0)

        tree.check_for_bad_dependencies()


class TestNumLevels(unittest.TestCase):
    maxDiff = 10000

    def test_no_levels(self):
        tree = Tree()
        self.assertEqual(tree.num_levels(), 0)

    def test_one_level(self):
        tree = Tree()
        tree.new_node("root")
        self.assertEqual(tree.num_levels(), 1)

    def test_two_spanning_levels(self):
        tree = Tree()
        for i in range(10):
            tree.new_node("root" + str(i))
            tree.new_node("branch" + str(i), "root" + str(i))
        self.assertEqual(tree.num_levels(), 2)


class TestChildOf(unittest.TestCase):
    maxDiff = 10000

    def test_root_child_of_leaf(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        self.assertFalse(tree.child_of("Shem", "Peleg"))

    def test_leaf_child_of_root(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        self.assertTrue(tree.child_of("Peleg", "Shem"))

    def test_leaf_child_of_other_leaf(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        self.assertFalse(tree.child_of("Peleg", "Lud"))


class TestGetRootsNodesAndLeaves(unittest.TestCase):
    maxDiff = 10000

    def test_get_roots(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.unparent("Eber")
        self.assertEqual(set(tree.get_roots()), set(["Shem", "Eber"]))

    def test_get_nodes(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        self.assertEqual(set(tree.get_nodes()), set(["Adam", "Cain", "Abel", "Seth", "Enoch"]))

    def test_get_leaves(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        self.assertEqual(set(tree.get_leaves()), set(["Seth", "Abel", "Enoch"]))


class TestGetRoot(unittest.TestCase):
    maxDiff = 10000

    def test_get_enochs_root(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        self.assertEqual(tree.get_root("Enoch"), "Adam")

    def test_get_invalid_node_root(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        with self.assertRaises(KeyError):
            tree.get_root("Esau")

    def test_get_adams_root(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        self.assertEqual(tree.get_root("Adam"), "Adam")


class TestClear(unittest.TestCase):
    maxDiff = 10000

    def test_with_tree(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        tree.clear()
        self.assertEqual(tree.nodes, {})

    def test_without_tree(self):
        tree = Tree()
        tree.clear()
        self.assertEqual(tree.nodes, {})


class TestGetLevels(unittest.TestCase):
    maxDiff = 10000

    def test_empty_tree(self):
        tree = Tree()
        self.assertEqual(tree.get_level(10), [])

    def test_get_roots(self):
        tree = Tree()
        self.assertEqual(tree.get_level(0), tree.get_roots())

    def test_get_enoch(self):
        tree = Tree()
        tree = add_adam_nodes(tree)
        self.assertEqual(tree.get_level(2), ["Enoch"])


class TestLoopingDependenciesCheck(unittest.TestCase):
    maxDiff = 10000

    def test_empty_tree(self):
        tree = Tree()
        tree.check_for_bad_dependencies()

    def test_rebellious_child(self):
        tree = Tree()
        tree.new_node("Parent")
        tree.new_node("Child")

        # never access tree.nodes outside of test cases!\
        tree.nodes["Parent"]['children'].add("Child")

        with self.assertRaises(RebelChildError):
            tree.check_for_bad_dependencies()

    def test_parented_to_self(self):
        tree = Tree()
        tree.new_node("A")

        # never access tree.nodes outside of test cases!
        tree.nodes["A"]['parent'] = "A"

        with self.assertRaises(LoopInTreeError):
            tree.check_for_bad_dependencies()

    def test_two_node_loop(self):
        tree = Tree()
        tree.new_node("A")
        tree.new_node("B")

        # never access tree.nodes outside of test cases!
        tree.nodes["A"]['parent'] = "B"
        tree.nodes["B"]['parent'] = "A"

        with self.assertRaises(LoopInTreeError):
            tree.check_for_bad_dependencies()

    def test_three_node_loop(self):
        """
        Should be:

        A --> B --> C

        But it's a cyclic loop instead:

        A --> B --> C
        |           |
        +-----<-----+

        This is what we should be checking for :)
        """
        tree = Tree()
        tree.new_node("A")
        tree.new_node("B")
        tree.new_node("C")

        # never access tree.nodes outside of test cases!
        tree.nodes["A"]['parent'] = "B"
        tree.nodes["B"]['parent'] = "C"
        tree.nodes["C"]['parent'] = "A"

        with self.assertRaises(LoopInTreeError):
            tree.check_for_bad_dependencies()


if __name__ == "__main__":
    unittest.main()
