#! /usr/bin/env python3
##
# Utils to emulate automark
##

def _walk(parts, data, parent):
    if len(parts) == 0:
        return data
    if len(parts) == 1:
        parent[parts[0]] = data
    else:
        head = parts[0]
        if head not in parent:
            parent[head] = dict()
        _walk(parts[1:], data, parent[head])

def deflatten(row, sep="_"):
    """Deflatten filter converts a flat dictionary into a tree-like structure"""
    out = dict()

    for key, value in row.items():
        parts = key.split(sep)
        _walk(parts, value, out)

    return out

def subtotal(cols, trigger="mark", key="total"):
    """Work out a total for answers formatted as: question => (trigger => score)"""
    total = 0
    
    for (question, val) in cols.items():
        if not isinstance(val, dict):
            continue

        if trigger in val:
            total += int(val[trigger])

    if key and key not in cols:
        cols[key] = total

    return total

def total(cols, trigger="mark", key="total"):
    """Work out a total for answers formatted as: part => (question => (trigger => score))"""
    total = 0

    for (part, question) in cols.items():
        total += subtotal(question)
    
    if key and key not in cols:
        cols[key] = total

    return total


def test():
    flattened = {
        "p1_q1_mark": 3,
        "p1_q1_comm": "cheese mark",
        "p1_q2_mark": 0,
        "p1_q2_comm": "fruit mark",

        "p2_q1_mark": 3,
        "p2_q1_comm": "cheese mark",
        "p2_q2_mark": 0,
        "p2_q2_comm": "fruit mark",
    }

    tree = deflatten(flattened)
    subtotal = subtotal(tree)

    print(tree)
