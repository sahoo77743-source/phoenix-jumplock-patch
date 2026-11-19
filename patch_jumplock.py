#!/usr/bin/env python3
"""If peak jumps past 1.50R before any profit stop exists, arm +0.50R immediately."""
import os
import shutil
import py_compile

TARGET = "main.py"
BACKUP = "main.py.bak_jumplock"

OLD = """    if peak < need or peak >= float(getattr(config, "RATCHET_START_R", 1.50)):
        return
"""

NEW = """    jumped = peak >= float(getattr(config, "RATCHET_START_R", 1.50))
    if peak < need:
        return
    if jumped:
        logger.info(f"⚡ jump lock {symbol} | peak={peak:.2f} → SL +{lock_r:.2f}R before ratchet")
"""


def main():
    if not os.path.exists(TARGET):
        print(f"STOPPED missing {TARGET}")
        return
    shutil.copy2(TARGET, BACKUP)
    text = open(TARGET, encoding="utf-8").read()
    n = text.count(OLD)
    if n != 1:
        shutil.copy2(BACKUP, TARGET)
        print(f"STOPPED piece count={n}")
        print(f"restored from {BACKUP} — bot file was not changed")
        return
    if "jump lock" in text:
        shutil.copy2(BACKUP, TARGET)
        print("STOPPED jump lock is already in this file")
        print(f"restored from {BACKUP} — bot file was not changed")
        return
    text = text.replace(OLD, NEW, 1)
    open(TARGET, "w", encoding="utf-8").write(text)
    try:
        py_compile.compile(TARGET, doraise=True)
    except Exception as e:
        shutil.copy2(BACKUP, TARGET)
        print(f"STOPPED compile: {e}")
        print(f"restored from {BACKUP} — bot file was not changed")
        return
    print("DONE pieces=1")
    print(f"backup={BACKUP}")


if __name__ == "__main__":
    main()
