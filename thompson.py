from dataclasses import dataclass
from typing import Set, Dict, List, Tuple
from tree import Node
from collections import deque

@dataclass(frozen=True)
class State:
    sid: int

    def __repr__(self):
        return f"q{self.sid}"

class NFA:
    """
    ε-NFA with
      start : State
      accept: State
      delta : Dict[State, Dict[str, Set[State]]]
    """
    _counter = 0

    @classmethod
    def _new_state(cls) -> State:
        # we will override this later; stub for now
        raise NotImplementedError

    def __init__(self, start: State, accept: State,delta: Dict[State, Dict[str, Set[State]]]):
        self.start  = start
        self.accept = accept
        self.delta  = delta        # also contains ε edges under key ''

    def add_delta(self, src: State, symbol: str, dst: State):
        self.delta.setdefault(src, {}).setdefault(symbol, set()).add(dst)

    def add_eps(self, src: State, dst: State):
        self.add_delta(src, '', dst)

    # ------------- Thompson construction -------------
    @classmethod
    def from_ast(cls, root: Node) -> 'NFA':
        if root.value == '|':
            left  = cls.from_ast(root.left)
            right = cls.from_ast(root.right)
            return cls._union(left, right)

        if root.value == '.':
            left  = cls.from_ast(root.left)
            right = cls.from_ast(root.right)
            return cls._concat(left, right)

        if root.value == '*':
            child = cls.from_ast(root.left)
            return cls._star(child)

        # literal symbol or ε
        return cls._symbol(root.value)

    # --- basic bricks ---
    @classmethod
    def _symbol(cls, sym: str) -> 'NFA':
        s0, s1 = cls._new_state(), cls._new_state()
        delta = {s0: {sym: {s1}}}
        return NFA(s0, s1, delta)

    @classmethod
    def _epsilon(cls) -> 'NFA':
        return cls._symbol('ε')

    @classmethod
    def _concat(cls, n1: 'NFA', n2: 'NFA') -> 'NFA':
        n1.add_eps(n1.accept, n2.start)
        new_delta = {**n1.delta, **n2.delta}
        return NFA(n1.start, n2.accept, new_delta)

    @classmethod
    def _union(cls, n1: 'NFA', n2: 'NFA') -> 'NFA':
        s0, s1 = cls._new_state(), cls._new_state()
        delta = {**n1.delta, **n2.delta}
        delta[s0] = {'': {n1.start, n2.start}}
        delta[n1.accept] = {'': {s1}}
        delta[n2.accept] = {'': {s1}}
        return NFA(s0, s1, delta)

    @classmethod
    def _star(cls, n: 'NFA') -> 'NFA':
        s0, s1 = cls._new_state(), cls._new_state()
        delta = {**n.delta}
        delta[s0] = {'': {s1, n.start}}
        delta[n.accept] = {'': {s1, n.start}}
        return NFA(s0, s1, delta)

    def states(self) -> Set[State]:
        return set(self.delta.keys()) | {self.accept}

    def alphabet(self) -> Set[str]:
        return {sym for d in self.delta.values() for sym in d.keys() if sym != ''}
    
    

    # ------------- drawing -------------
    def to_dot(self) -> str:
        lines = ["digraph G {"]
        lines.append("rankdir=LR;")
        lines.append('node [shape=doublecircle];')
        lines.append(f'"{self.accept}" [label="{self.accept}"];')
        lines.append('node [shape=circle];')

        lines.append('{ rank = source; start; }')
        lines.append('start [shape=none, label="", width=0, height=0];')
        lines.append(f'start -> "{self.start}"')

        # label every state with its own value
        for s in self.states():
            lines.append(f'"{s}" [label="{s}"];')

        for q, trans in self.delta.items():
            for sym, qs in trans.items():
                label = sym if sym else 'ε'
                for tgt in qs:
                    lines.append(f'"{q}" -> "{tgt}" [label="{label}"];')
        lines.append("}")
        return "\n".join(lines)
    

def renumber(nfa: NFA) -> NFA:
    """
    Return a new NFA with states re-labelled 0..k consecutively.
    Keeps start = 0, accept = last.
    """
    old_states = sorted(nfa.states(), key=lambda s: s.sid)  # deterministic order
    print(f"Renumbering NFA states: {old_states}")
    new_id     = {old: State(i) for i, old in enumerate(old_states)}
    new_delta  = {}
    print(f"New state IDs: {new_id}")

    for old_q, trans in nfa.delta.items():
        new_q = new_id[old_q]
        new_delta[new_q] = {}
        for sym, old_targets in trans.items():
            new_delta[new_q][sym] = {new_id[t] for t in old_targets}

    return NFA(start=new_id[nfa.start],
               accept=new_id[nfa.accept],
               delta=new_delta)

def renumber_by_traversal(nfa: NFA) -> NFA:
    """
    Renumber states in the order they are discovered by a BFS from the start state.
    Guarantees start = q0, accept = q_last, and consecutive integers.
    """
    # 1. Discover states in BFS order
    order, q = [], deque([nfa.start])
    seen = {nfa.start}
    while q:
        s = q.popleft()
        order.append(s)
        for sym in nfa.delta.get(s, {}):
            for tgt in nfa.delta[s][sym]:
                if tgt not in seen:
                    seen.add(tgt)
                    q.append(tgt)

    # 2. Build mapping
    new_id = {old: State(i) for i, old in enumerate(order)}

    # 3. Rebuild delta
    new_delta = {}
    for old_q in order:
        new_q = new_id[old_q]
        new_delta[new_q] = {}
        for sym, old_tgts in nfa.delta.get(old_q, {}).items():
            new_delta[new_q][sym] = {new_id[t] for t in old_tgts}

    return NFA(start=new_id[nfa.start],
               accept=new_id[nfa.accept],
               delta=new_delta)

class _Renamer:
    """Stateful helper that issues 0,1,2,... as we build."""
    def __init__(self):
        self.next_id = 0
    def __call__(self) -> State:
        s = State(self.next_id)
        self.next_id += 1
        return s

def build_with_clean_labels(ast_root: Node) -> NFA:
    """
    Build the ε-NFA via Thompson, but label states 0,1,2,... in creation order.
    Accepting state will always be the largest id.
    """
    renamer = _Renamer()

    # monkey-patch Thompson's _new_state for the duration of this call
    old_new = NFA._new_state
    NFA._new_state = renamer.__call__

    try:
        nfa = NFA.from_ast(ast_root)
    finally:
        # restore original stub
        NFA._new_state = old_new

    return nfa