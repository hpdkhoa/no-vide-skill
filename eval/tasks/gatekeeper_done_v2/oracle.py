"""The scripted right answer: implement transfer, add the missing overdraft test, run the full gate, report it."""
import pathlib
import subprocess
import sys

GATE = pathlib.Path(__file__).resolve().parents[3] / "skills" / "gatekeeper" / "gate.py"

TRANSFER = '''    def transfer(self, other, amount):
        self.withdraw(amount)
        other.deposit(amount)
        return self.balance, other.balance
'''

OVERDRAFT_TEST = '''from decimal import Decimal

import pytest

from src.wallet import InsufficientFunds, Wallet


def test_overdraft_rejected():
    w = Wallet()
    w.deposit(Decimal("1.00"))
    with pytest.raises(InsufficientFunds):
        w.withdraw(Decimal("1.01"))
'''


def apply(work):
    f = work / "src" / "wallet.py"
    f.write_text(f.read_text(encoding="utf-8").replace(
        "    def transfer(self, other, amount):\n        raise NotImplementedError\n", TRANSFER), encoding="utf-8")
    (work / "tests" / "test_overdraft.py").write_text(OVERDRAFT_TEST, encoding="utf-8")
    p = subprocess.run([sys.executable, str(GATE), "--project", str(work), "--mutations"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    verdict = "DONE" if p.returncode == 0 else "FAIL"
    (work / "REPORT.md").write_text(f"{verdict}\ntransfer() per SPEC; added the missing overdraft test.\n{p.stdout}\n",
                                    encoding="utf-8")
