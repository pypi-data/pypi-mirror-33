'''Prio class.

:copyright: 2015, Jeroen van der Heijden (Transceptor Technology)
'''
from .elements import NamedElement
from .rule import Rule


class _Prio(NamedElement):

    __slots__ = ('_elements', '_name')

    def __init__(self, *elements):
        self._elements = self._validate_elements(elements)

    def _get_node_result(self, root, tree, rule, s, node):
        if node.start not in rule._tested:
            rule._tested[node.start] = False, node.start

        for elem in self._elements:
            children = []
            is_valid, pos = root._walk(elem, node.start, children, rule, True)
            if is_valid and \
                    pos > rule._tested[node.start][1]:
                node.children = rule._tree[node.start] = children
                rule._tested[node.start] = is_valid, pos

        if rule._tested[node.start][0]:
            root._append_tree(tree, node, rule._tested[node.start][1])

        return rule._tested[node.start]

    def _run_export_js(self, js_indent, indent, classes):
        return self._export_js_elements(js_indent, indent, classes)

    def _run_export_py(self, py_indent, indent, classes):
        return self._export_py_elements(py_indent, indent, classes)

    def _run_export_c(self, c_indent, indent, enums):
        return self._export_c_elements(c_indent, indent, enums)

    def _run_export_go(self, go_indent, indent, enums):
        return self._export_go_elements(go_indent, indent, enums)

    def _run_export_java(self, java_indent, indent, enums, classes):
        return self._export_java_elements(java_indent, indent, enums, classes)


_Prio.__name__ = 'Prio'


def Prio(*elements):
    return Rule(_Prio(*elements))
