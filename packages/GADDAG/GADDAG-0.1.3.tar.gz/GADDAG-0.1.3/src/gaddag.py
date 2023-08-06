import ctypes
import os

PATH = os.path.dirname(__file__)
cgaddag = ctypes.cdll.LoadLibrary(os.path.join(PATH, "cgaddag.so"))


class cEdge(ctypes.Structure):
    pass


class cNode(ctypes.Structure):
    pass


class cList(ctypes.Structure):
    pass


cEdge._fields_ = [("ch", ctypes.c_char_p),
                  ("node", ctypes.POINTER(cNode)),
                  ("next", ctypes.POINTER(cEdge))]

cNode._fields_ = [("edges", ctypes.POINTER(cEdge)),
                  ("end", ctypes.c_int)]

cList._fields_ = [("str", ctypes.c_char_p),
                  ("next", ctypes.POINTER(cList))]


class cGADDAG(ctypes.Structure):
    _fields_ = [("root", ctypes.POINTER(cNode)),
                ("length", ctypes.c_int)]


class Node():
    """A node in a GADDAG."""
    def __init__(self, cnode):
        self.contents = cnode.contents

    def __str__(self):
        return "[{}] {}".format(", ".join(sorted([edge for edge in self])),
                                self.is_end)

    def __iter__(self):
        for char in self.edges:
            yield char

    def __len__(self):
        return len(self.edges)

    def __contains__(self, char):
        char = char.lower()
        return char in self.edges

    def __getitem__(self, char):
        char = char.lower()
        cgaddag.find_edge.restype = ctypes.POINTER(cEdge)
        cgaddag.find_edge.argtypes = [ctypes.POINTER(cNode), ctypes.c_char]
        edge = cgaddag.find_edge(self.contents, char.encode("ascii"))

        if not edge:
            raise KeyError(char)

        return Node(edge.contents.node)

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        if self.is_end != other.is_end or self.edges != other.edges:
            return False

        for child in self:
            if self[child] != other[child]:
                return False

        return True

    @property
    def edges(self):
        """Return the edges of this node."""
        edges = set()
        edge = self.contents.edges
        while edge:
            edges.add(edge.contents.ch.decode("ascii"))
            edge = edge.contents.next
        return edges

    @property
    def is_end(self):
        """Return `True` if this node is an end node, `False` otherwise."""
        return bool(self.contents.end)

    def follow(self, chars):
        """
        Traverse the GADDAG to the node at the end of the given characters.

        Args:
            chars: An string of characters to traverse in the GADDAG.

        Returns:
            The Node which is found by traversing the tree.
        """
        cgaddag.follow_edge.restype = ctypes.POINTER(cNode)
        cgaddag.follow_edge.argtypes = [ctypes.POINTER(cNode), ctypes.c_char]

        node = self.contents
        for char in chars:
            node = cgaddag.follow_edge(node, char.encode("ascii"))
            if not node:
                raise KeyError(char)

        return Node(node)


class GADDAG():
    """A data structure that allows extremely fast searching of words."""
    def __init__(self, words=None):
        cgaddag.newGADDAG.restype = ctypes.POINTER(cGADDAG)
        self.gdg = cgaddag.newGADDAG().contents

        if words:
            if type(words) is str:
                raise TypeError("Input must be an iterable of strings")

            for word in words:
                self._add_word(word)

    def __len__(self):
        return self.gdg.length

    def __contains__(self, word):
        cgaddag.has.restype = ctypes.c_bool
        cgaddag.has.argtypes = [ctypes.POINTER(cGADDAG), ctypes.c_char_p]

        word = word.lower()

        return cgaddag.has(self.gdg, word.encode(encoding="ascii"))

    def __iter__(self):
        return self.ends_with("")

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        if len(self) != len(other):
            return False

        return self.root == other.root

    @property
    def root(self):
        """Returns the root node of the GADDAG."""
        return Node(self.gdg.root)

    def contains(self, sub):
        """
        Find all words containing a substring.

        Args:
            sub: A substring to be searched for.

        Returns:
            A set of all words found.
        """
        cgaddag.contains.restype = ctypes.POINTER(cList)
        cgaddag.contains.argtypes = [ctypes.POINTER(cGADDAG), ctypes.c_char_p]

        sub = sub.lower()

        found_words = set()

        res = cgaddag.contains(self.gdg, sub.encode(encoding="ascii"))

        while res:
            if res.contents.str not in found_words:
                found_words.add(res.contents.str)
                yield res.contents.str.decode("ascii")
            res = res.contents.next

    def starts_with(self, prefix):
        """
        Find all words starting with a prefix.

        Args:
            prefix: A prefix to be searched for.

        Returns:
            A set of all words found.
        """
        cgaddag.starts_with.restype = ctypes.POINTER(cList)
        cgaddag.starts_with.argtypes = [ctypes.POINTER(cGADDAG),
                                        ctypes.c_char_p]

        prefix = prefix.lower()

        res = cgaddag.starts_with(self.gdg, prefix.encode(encoding="ascii"))

        while res:
            yield res.contents.str.decode("ascii")
            res = res.contents.next

    def ends_with(self, suffix):
        """
        Find all words ending with a suffix.

        Args:
            suffix: A suffix to be searched for.

        Returns:
            A set of all words found.
        """
        cgaddag.ends_with.restype = ctypes.POINTER(cList)
        cgaddag.ends_with.argtypes = [ctypes.POINTER(cGADDAG), ctypes.c_char_p]

        suffix = suffix.lower()

        res = cgaddag.ends_with(self.gdg, suffix.encode(encoding="ascii"))

        while res:
            yield res.contents.str.decode("ascii")
            res = res.contents.next

    def _add_word(self, word):
        """
        Add a word to the GADDAG.

        Args:
            word: A word to be added to the GADDAG.
        """
        cgaddag.add_word.restype = ctypes.c_void_p
        cgaddag.add_word.argtypes = [ctypes.POINTER(cGADDAG), ctypes.c_char_p]

        word = word.lower()

        word = word.encode(encoding="ascii")

        cgaddag.add_word(self.gdg, word)
