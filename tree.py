# tree_builder.py
import graphviz
from typing import List, Optional

# --------------------------------------------------------------------------------
# Nodo para el árbol sintáctico
# --------------------------------------------------------------------------------
class Node:
    def __init__(self, value: str, left: Optional['Node'] = None, right: Optional['Node'] = None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return str(self.value)

# --------------------------------------------------------------------------------
# Construye el árbol a partir de un postfix
# --------------------------------------------------------------------------------
def build_ast(postfix: str) -> Node:
    stack: List[Node] = []
    for ch in postfix:
        if ch in {'|', '.'}:            # operadores binarios
            right = stack.pop()
            left  = stack.pop()
            stack.append(Node(ch, left, right))
        elif ch == '*':                 # operador unario
            child = stack.pop()
            stack.append(Node(ch, child))
        else:                           # símbolo o ε
            stack.append(Node(ch))
    if len(stack) != 1:
        raise ValueError("Expresión postfix mal formada")
    return stack[0]

# --------------------------------------------------------------------------------
# Genera la gráfica con Graphviz
# --------------------------------------------------------------------------------
def render_tree(root: Node, filename: str = "ast") -> None:
    dot = graphviz.Digraph(format="png")
    counter = 0

    def _id():
        nonlocal counter
        counter += 1
        return str(counter)

    def add_nodes(node: Optional[Node]):
        if node is None:
            return
        node_id = _id()
        dot.node(node_id, str(node.value))

        if node.left:
            left_id = add_nodes(node.left)
            dot.edge(node_id, left_id, label="L")
        if node.right:
            right_id = add_nodes(node.right)
            dot.edge(node_id, right_id, label="R")
        return node_id

    add_nodes(root)
    dot.render(filename, view=True, cleanup=True)

# --------------------------------------------------------------------------------
# Ejemplo de uso (se puede ejecutar directamente)
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # postfix obtenido en el paso anterior
    postfix = "ae|0|3|ae|0|3|*..ae|0|3|.ae|0|3|*...co.m.ne.t.|or.g.|..gt.cr.|co.|..ε|."
    tree = build_ast(postfix)
    render_tree(tree, "ast_regex")


