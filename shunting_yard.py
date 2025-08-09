import re
from tree import Node # for Node class

# 1.  REGEX NORMALIZER  -------------------------------------------------------
def normalize(regex: str) -> str:
    """
    Expands:
        a+  -> a a*
        a?  -> (a|ε)
        […] -> (…|…)
    Works correctly even when '+' applies to a parenthesised expression.
    """
    out = list(regex)
    i = 0
    while i < len(out):
        c = out[i]

        # --- escapes ----------------------------------------------------------
        if c == '\\' and i + 1 < len(out):
            i += 2
            continue

        # --- character classes ------------------------------------------------
        if c == '[':
            j = i + 1
            content = ""
            while j < len(out) and out[j] != ']':
                if j + 2 < len(out) and out[j + 1] == '-':
                    start, end = out[j], out[j + 2]
                    content += ''.join(chr(k) for k in range(ord(start), ord(end) + 1))
                    j += 3
                else:
                    content += out[j]
                    j += 1
            # replace […] with (…|…)
            replacement = ['('] + list('|'.join(content)) + [')']
            out[i:j + 1] = replacement
            i += len(replacement)
            continue

        # --- plus operator ----------------------------------------------------
        if c == '+':
            # find the balanced expression that precedes the +
            start = i - 1
            balance = 0
            while start >= 0:
                if out[start] == ')':
                    balance += 1
                elif out[start] == '(':
                    balance -= 1
                    if balance < 0:
                        break
                if balance == 0:
                    break
                start -= 1
            else:
                start = i - 1  # simple single character

            expr = out[start:i]
            # replace E+ with E E*
            out[start:i + 1] = expr + expr + ['*']
            i = start + 2 * len(expr) + 1
            continue

        # --- optional operator ------------------------------------------------
        if c == '?':
            start = i - 1
            balance = 0
            while start >= 0:
                if out[start] == ')':
                    balance += 1
                elif out[start] == '(':
                    balance -= 1
                    if balance < 0:
                        break
                if balance == 0:
                    break
                start -= 1
            else:
                start = i - 1

            expr = out[start:i]
            # replace E? with (E|ε)
            out[start:i + 1] = ['('] + expr + ['|', 'ε', ')']
            i = start + len(expr) + 4
            continue

        i += 1

    return ''.join(out)


# 2.  INFIX → POSTFIX  (Shunting-Yard adaptado) --------------------------------
SPECIAL = {'|', '.', '*', '(', ')', 'ε'}

def precedence(op):
    return {'|': 1, '.': 2, '*': 3}.get(op, 0)

def add_explicit_concat(regex: str) -> list[str]:
    token_re = re.compile(r'ε|\\.|[a-zA-Z0-9]+|[()|*]')
    tokens   = token_re.findall(regex)

    out = []
    for i, tok in enumerate(tokens):
        out.append(tok)
        if i + 1 == len(tokens):
            break
        nxt = tokens[i + 1]

        # insert dot between operand and operand
        left_operand  = tok not in {'|', '(', '.'}
        right_operand = nxt not in {'|', ')', '*', '+', '?', '.'}
        if left_operand and right_operand:
            out.append('.')
    return out  



def infix_to_postfix(regex: str) -> list[str]:
    tokens = add_explicit_concat(regex)   # list already dotted
    stack, out = [], []
    for tok in tokens:
        if tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            stack.pop()
        elif tok in {'|', '.', '*'}:
            while stack and precedence(stack[-1]) >= precedence(tok):
                out.append(stack.pop())
            stack.append(tok)
        else:                           # literal / ε
            out.append(tok)
    while stack:
        out.append(stack.pop())
    return out          # <-- list of tokens

def tokenize(expr: str):
    token_re = re.compile(r'ε|\\.|[a-zA-Z0-9]+|[()|*]')
    return token_re.findall(expr)

def build_ast(postfix: list[str]) -> Node:
    stack = []
    for tok in postfix:
        if tok in {'|', '.'}:          # binary
            right = stack.pop()
            left  = stack.pop()
            stack.append(Node(tok, left, right))
        elif tok == '*':               # unary
            child = stack.pop()
            stack.append(Node(tok, child))
        else:                          # literal / ε
            stack.append(Node(tok))
    if len(stack) != 1:
        raise ValueError("Expresión postfix mal formada")
    return stack[0]


# 3.  DEMO ----------------------------------------------------------------------
if __name__ == "__main__":
    
    file = open("infix.txt", "r", encoding='utf-8')
    for line in file:
        original = line.strip()
        print("Original :", original)
        norm = normalize(original)
        print("Normal   :", norm)
        postfix = infix_to_postfix(norm)
        print("Postfix  :", postfix)
    

    

