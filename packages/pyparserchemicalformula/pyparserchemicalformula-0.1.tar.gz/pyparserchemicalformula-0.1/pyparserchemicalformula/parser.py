#!/usr/bin/env python

import re
from collections import Counter

from pyparserchemicalformula.contants import ATOM_REGEX, OPENERS, CLOSERS


def is_balanced(formula):
    """Check if all sort of brackets come in pairs.

    @param formula: The forumla to parse
    @type formula: str

    @return: Result of sort of brackets come in pairs
    @rtype : bool
    """
    counter = Counter(formula)
    result = counter[
        '['] == counter[']'] and counter['{'] == counter[
            '}'] and counter['('] == counter[')']

    return result


def _dictify(tuples):
    res = {}

    for atom, n in tuples:
        if atom in res:
            res[atom] += int(n or 1)
        else:
            res[atom] = int(n or 1)

    return res


def _fuse(mol1, mol2, w=1):
    return {
        atom: (
            mol1.get(atom, 0) + mol2.get(
                atom, 0)) * w for atom in set(mol1) | set(mol2)}


def _parse(formula):
    element = []
    mol = {}
    index = 0

    while index < len(formula):
        token = formula[index]

        if token in CLOSERS:
            match = re.match('\d+', formula[index+1:])

            if match:
                weight = int(match.group(0))
                index += len(match.group(0))
            else:
                weight = 1

            submol = _dictify(re.findall(ATOM_REGEX, ''.join(element)))

            return _fuse(mol, submol, weight), index

        elif token in OPENERS:
            submol, count = _parse(formula[index+1:])
            mol = _fuse(mol, submol)
            index += count + 1
        else:
            element.append(token)

        index += 1

    return _fuse(
        mol, _dictify(re.findall(ATOM_REGEX, ''.join(element)))), index


def parse_molecule(formula):
    """Parse the formula and return a dict with occurences of each atom.

    @param formula: The forumla to parse
    @type formula: str

    @return: The result of the forumla
    @rtype : dict

    @raise ValueError: The formula is invalid
    """
    """Parse the formula and return a dict with occurences of each atom"""
    if not is_balanced(formula):
        raise ValueError("Watch your brackets ![{]$[&?)]}!]")

    return _parse(formula)[0]
