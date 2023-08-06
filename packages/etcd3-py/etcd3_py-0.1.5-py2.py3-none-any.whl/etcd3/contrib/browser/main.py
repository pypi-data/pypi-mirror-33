#!/usr/bin/python
# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.
import os

import urwid

# define some colours
palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
    ('bars', 'dark blue', 'light gray', ''),
    ('arrowtip', 'light blue', 'light gray', ''),
    ('connectors', 'light red', 'light gray', ''),
]


# We use selectable Text widgets for our example..


class FocusableText(urwid.WidgetWrap):
    """Selectable Text used for nodes in our example"""

    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


# define a test tree in the format accepted by SimpleTree. Essentially, a
# tree is given as (nodewidget, [list, of, subtrees]). SimpleTree accepts
# lists of such trees.


def construct_example_simpletree_structure(selectable_nodes=True, children=3):
    Text = FocusableText if selectable_nodes else urwid.Text

    # define root node
    tree = (Text('ROOT'), [])

    # define some children
    c = g = gg = 0  # counter
    for i in range(children):
        subtree = (Text('Child {0:d}'.format(c)), [])
        # and grandchildren..
        for j in range(children):
            subsubtree = (Text('Grandchild {0:d}'.format(g)), [])
            for k in range(children):
                leaf = (Text('Grand Grandchild {0:d}'.format(gg)), None)
                subsubtree[1].append(leaf)
                gg += 1  # inc grand-grandchild counter
            subtree[1].append(subsubtree)
            g += 1  # inc grandchild counter
        tree[1].append(subtree)
        c += 1
    return tree


def construct_example_tree(selectable_nodes=True, children=2):
    # define a list of tree structures to be passed on to SimpleTree
    forrest = [construct_example_simpletree_structure(selectable_nodes,
                                                      children)]

    # stick out test tree into a SimpleTree and return
    return SimpleTree(forrest)


def unhandled_input(k):
    # exit on q
    if k in ['q', 'Q']: raise urwid.ExitMainLoop()


import urwid
from urwidtrees.tree import Tree


# define selectable urwid.Text widgets to display paths
class FocusableText(urwid.WidgetWrap):
    """Widget to display paths lines"""

    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


# define Tree that can walk your filesystem


class DirectoryTree(Tree):
    """
    A custom Tree representing our filesystem structure.
    This implementation is rather inefficient: basically every position-lookup
    will call `os.listdir`.. This makes navigation in the tree quite slow.
    In real life you'd want to do some caching.
    As positions we use absolute path strings.
    """
    # determine dir separator and form of root node
    pathsep = os.path.sep
    drive, _ = os.path.splitdrive(pathsep)

    # define root node This is part of the Tree API!
    root = drive + pathsep

    def __getitem__(self, pos):
        return FocusableText(pos)

    # generic helper
    def _list_dir(self, path):
        """returns absolute paths for all entries in a directory"""
        try:
            elements = [os.path.join(
                path, x) for x in os.listdir(path) if os.path.isdir(path)]
            elements.sort()
        except OSError:
            elements = None
        return elements

    def _get_siblings(self, pos):
        """lists the parent directory of pos """
        parent = self.parent_position(pos)
        siblings = [pos]
        if parent is not None:
            siblings = self._list_dir(parent)
        return siblings

    # Tree API
    def parent_position(self, pos):
        parent = None
        if pos != '/':
            parent = os.path.split(pos)[0]
        return parent

    def first_child_position(self, pos):
        candidate = None
        if os.path.isdir(pos):
            children = self._list_dir(pos)
            if children:
                candidate = children[0]
        return candidate

    def last_child_position(self, pos):
        candidate = None
        if os.path.isdir(pos):
            children = self._list_dir(pos)
            if children:
                candidate = children[-1]
        return candidate

    def next_sibling_position(self, pos):
        candidate = None
        siblings = self._get_siblings(pos)
        myindex = siblings.index(pos)
        if myindex + 1 < len(siblings):  # pos is not the last entry
            candidate = siblings[myindex + 1]
        return candidate

    def prev_sibling_position(self, pos):
        candidate = None
        siblings = self._get_siblings(pos)
        myindex = siblings.index(pos)
        if myindex > 0:  # pos is not the first entry
            candidate = siblings[myindex - 1]
        return candidate


from urwidtrees.widgets import TreeBox
from urwidtrees.tree import SimpleTree
from urwidtrees.nested import NestedTree
from urwidtrees.decoration import ArrowTree, CollapsibleArrowTree  # decoration
import urwid

if __name__ == "__main__":
    # logging.basicConfig(filename='example.log',level=logging.DEBUG)
    # Take some Arrow decorated Tree that we later stick inside another tree.
    innertree = ArrowTree(construct_example_tree())
    # Some collapsible, arrow decorated tree with extra indent
    anotherinnertree = CollapsibleArrowTree(construct_example_tree(),
                                            indent=10)

    # A SimpleTree, that contains the two above
    middletree = SimpleTree(
        [
            (FocusableText('Middle ROOT'),
             [
                 (FocusableText('Mid Child One'), None),
                 (FocusableText('Mid Child Two'), None),
                 (innertree, None),
                 (FocusableText('Mid Child Three'),
                  [
                      (FocusableText('Mid Grandchild One'), None),
                      (FocusableText('Mid Grandchild Two'), None),
                  ]
                  ),
                 (anotherinnertree,
                  # middletree defines a childnode here. This is usually
                  # covered by the tree 'anotherinnertree', unless the
                  # interepreting NestedTree's constructor gets parameter
                  # interpret_covered=True..
                  [
                      (FocusableText('XXX I\'m invisible!'), None),

                  ]),
             ]
             )
        ]
    )  # end SimpleTree constructor for middletree
    # use customized arrow decoration for middle tree
    middletree = ArrowTree(middletree,
                           arrow_hbar_char=u'\u2550',
                           arrow_vbar_char=u'\u2551',
                           arrow_tip_char=u'\u25B7',
                           arrow_connector_tchar=u'\u2560',
                           arrow_connector_lchar=u'\u255A')

    # define outmost tree
    outertree = SimpleTree(
        [
            (FocusableText('Outer ROOT'),
             [
                 (FocusableText('Child One'), None),
                 (middletree, None),
                 (FocusableText('last outer child'), None),
             ]
             )
        ]
    )  # end SimpleTree constructor

    # add some Arrow decoration
    outertree = ArrowTree(outertree)
    # wrap the whole thing into a Nested Tree
    outertree = NestedTree(outertree,
                           # show covered nodes like  XXX
                           interpret_covered=False
                           )

    # put it into a treebox and run
    treebox = TreeBox(outertree)
    rootwidget = urwid.AttrMap(treebox, 'body')
    # add a text footer
    footer = urwid.AttrMap(urwid.Text('Q to quit'), 'focus')
    # enclose all in a frame
    urwid.MainLoop(urwid.Frame(rootwidget, footer=footer), palette, unhandled_input=unhandled_input).run()  # go
