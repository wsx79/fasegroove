#!/usr/bin/env python3
"""Reject duplicate keys within each effective translation table.

A product may override common texts; it may not silently override its own earlier
rows. All product catalogs are combined in the same order as Product.cpp.
"""
import argparse
import json
from pathlib import Path
import re
import sys


def rows(files):
    seen = {}
    for path in files:
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.lstrip().startswith('{'):
                continue
            strings = re.findall(r'"(?:[^"\\]|\\.)*"', line)
            if len(strings) != 6:
                raise ValueError(f'{path}:{number}: expected six translation columns')
            values = tuple(json.loads(value) for value in strings)
            key = values[0]
            if key in seen:
                old = seen[key]
                raise ValueError(f'{path}:{number}: duplicate key {key!r}; first at {old}')
            seen[key] = f'{path}:{number}'
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.product.resolve()
    try:
        common = rows([root / 'ThirdParty/fasegroove-common/CommonTranslations.inc'])
        catalogs = [root / 'Source/Translations.inc']
        extra = root / 'Source/ArrangerTranslations.inc'
        if extra.exists():
            catalogs.append(extra)
        own = rows(catalogs)
    except (OSError, ValueError) as error:
        print(f'FAIL {error}', file=sys.stderr)
        return 1
    print(f'PASS translations: {len(common)} common, {len(own)} product keys; '
          f'{len(common.keys() & own.keys())} explicit product overrides')
    return 0


if __name__ == '__main__':
    sys.exit(main())
