import unittest

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
    maxDiff = None

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
    maxDiff = None

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


class TestDetaching(unittest.TestCase):
    maxDiff = None

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

    def test_replacement_shift_detach_arphaxad(self):
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

    def test_replacement_shift_detach_eber(self):
        tree = Tree()
        tree = add_shem_nodes(tree)
        tree.replacement_child_shift_detach("Eber")
        ebers_kids = ["Peleg", "Joktan"]

        for salah_kid in tree.nodes["Salah"]['children']:
            break
        self.assertIn(salah_kid, ebers_kids)

        self.assertEqual(set(tree.get_roots()), set(["Shem", "Eber"]))

        leaves = tree.get_leaves()
        names = ["Uz", "Hul", "Mash", "Gether", "Lud", "Asshur", "Elam"]
        self.assertEqual(len(names) + 1, len(leaves))
        for name in names:
            self.assertIn(name, leaves)
            leaves.remove(name)
        self.assertEqual(1, len(leaves))
        self.assertIn(leaves[0], ["Peleg", "Joktan"])


class TestNumLevels(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
