from typing import Set, Dict, List
from thompson import NFA, State

def epsilon_closure(states: Set[State], nfa: NFA) -> Set[State]:
    closure = set(states)
    stack   = list(states)
    while stack:
        q = stack.pop()
        for r in nfa.delta.get(q, {}).get('', set()):
            if r not in closure:
                closure.add(r)
                stack.append(r)
    return closure

def move(states: Set[State], symbol: str, nfa: NFA) -> Set[State]:
    res = set()
    for q in states:
        res |= nfa.delta.get(q, {}).get(symbol, set())
    return res

def accepts(nfa: NFA, word: str) -> bool:
    current = epsilon_closure({nfa.start}, nfa)
    for ch in word:
        current = epsilon_closure(move(current, ch, nfa), nfa)
    return nfa.accept in current