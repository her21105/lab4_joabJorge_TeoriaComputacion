from tree import build_ast, render_tree
from shunting_yard import infix_to_postfix, normalize
import graphviz
from thompson import NFA, renumber, build_with_clean_labels, State
from nfa import accepts
from collections import deque

with open("infix.txt", "r", encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        original = line.strip()
        if not original:
            continue
        print("\n" + "="*50)
        print("Regex:", original)

        norm    = normalize(original)
        postfix = infix_to_postfix(norm)
        ast     = build_ast(postfix)
        #render_tree(ast)

        # Build NFA
        NFA._counter = 0   
        nfa = build_with_clean_labels(ast)
  
        
        # Save NFA graph
        dot_src = nfa.to_dot()
        g = graphviz.Source(dot_src)
        nfa_file = f"nfa_{idx:03d}"
        g.render(nfa_file, format='png', cleanup=True)
        print(f"NFA saved to {nfa_file}.png")

        while True:
            renumber_choice = input("Renumber states? (y/n): ").strip().lower()
            if renumber_choice in {'y', 'n'}:
                break
            print("Please enter 'y' or 'n'.")
            # Simulation
            w = input("Enter string w to test: ").strip()
            if accepts(nfa, w):
                print("sí")
            else:
                print("no")

        