from tree import build_ast, render_tree
from shunting_yard import infix_to_postfix, normalize


with open("infix.txt", "r", encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        original = line.strip()
        print("Original :", original)
        if not original:
            continue

        norm    = normalize(original)
        print("Normal   :", norm)
        postfix = infix_to_postfix(norm)
        print("Postfix  :", postfix)
        ast     = build_ast(postfix)

        filename = f"ast_{idx:03d}"      # ast_001.png, ast_002.png, …
        render_tree(ast, filename)       # graphviz will create ast_001.png, etc.