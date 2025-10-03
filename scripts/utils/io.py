#!/usr/bin/env python3
from __future__ import annotations
import csv, os
from typing import Iterable, List
def safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
def write_text(path: str, text: str) -> None:
    safe_mkdir(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
def write_csv(path: str, rows: Iterable[List[str]]) -> None:
    safe_mkdir(os.path.dirname(path))
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)
