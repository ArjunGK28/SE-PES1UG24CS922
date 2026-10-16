# Lab 5: Static Code Analysis — Issue Log

**File:** `loan_calculator.py`
**Tools:** Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1 (Python 3.13)
**Baseline:** Pylint 5.17/10 · Bandit 8 issues (2 High, 1 Medium, 5 Low) · Flake8 22 issues
**Raw reports:** [`reports/before/`](reports/before/)

Line numbers refer to the original (unmodified) file. Rows are ordered by severity, highest first.

## Issue table

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Insecure FTP transfer | Security | Bandit B402, B321 | High | 3, 68–71 | `ftplib.FTP` sends the bureau credentials and the report file in plain text (CWE-319). | Switch to `ftplib.FTP_TLS` and call `prot_p()` so both the login and the data channel are encrypted. |
| 2 | Wrong eligibility logic (`or` instead of `and`) | Logic bug | — (found by running) | High | 24 | `credit_score > 750 or income > 25000` approves anyone who meets *either* condition and returns before the FOIR and loan-type checks run. The demo approves an unknown `"crypto"` loan, and approves a customer whose EMIs are 80% of their income. | Remove the early `return True`. Check FOIR and the allowed loan types first, then require a minimum score and income. |
| 3 | Rate passed as a percentage | Logic bug | — (found by running) | High | 94 | `calculate_emi(500000, 9, 5)` passes `9` (900%) where every other call uses a fraction (`0.09`). The EMI prints as 375000 when it should be about 10,379. | Pass `0.09`. Also add a check in `calculate_emi` that rejects a rate ≥ 1 and handles a 0% rate. |
| 4 | Max loan ignores interest | Logic bug | — / Pylint W0613, W0612 | High | 33–38 | It adds the monthly surplus once for each month (15000 × 60 = 900000) and never uses `annual_rate`. Pylint flags `annual_rate` as an unused argument, which points to this bug. The real figure is about 722,600. | Use the present-value-of-annuity formula: `available × (1 − (1 + r)^−n) / r`. |
| 5 | Interest saved includes principal | Logic bug | — (found by running) | High | 76–79 | It subtracts the two total repayments, so the ₹50,000 prepayment itself is counted as "interest saved" (prints 62275; the real figure is about 12,275). | Subtract the prepayment: `(original − reduced) − prepayment`. |
| 6 | Unsafe deserialisation with `marshal` | Security | Bandit B302 | Medium | 4, 57, 64 | `marshal.loads` on a file that could be tampered with is unsafe (CWE-502), and the format isn't stable across Python versions. | Use `json.dump` / `json.load`, which only produces plain data. |
| 7 | Mutable default argument | Bug | Pylint W0102 | Medium | 20–21 | `history=[]` is created once and shared by every call, so loan types from earlier calls pile up in it. | Default to `None` and create a new list inside the function. |
| 8 | Credit score range not validated | Logic bug | — (found by running) | Medium | 81–91 | Indian bureau scores (CIBIL) run from 300 to 900, but 950 is graded `"LOW"` risk. | Return `"INVALID"` for scores outside 300–900 before grading. |
| 9 | Division by zero | Bug | — | Medium | 26 | `existing_emi / income` crashes when `income` is 0. | Reject `income <= 0` before the FOIR check. |
| 10 | Hard-coded credential | Security | Bandit B107 | Low (Bandit) / High (real-world) | 67 | The FTP password `"Bureau#2024"` is in the source code, so anyone who can read the repo can see it (CWE-259). | Read the username and password from environment variables (`BUREAU_USER`, `BUREAU_PASSWORD`) and fail clearly if they aren't set. |
| 11 | Files opened without `with` | Bug | Pylint R1732 | Medium | 56, 63, 70 | If an exception is raised before `close()`, the file handle leaks. On line 70 the file is never closed. | Use `with open(...) as f:` everywhere. |
| 12 | `global` statement | Design | Pylint W0603 | Medium | 62 | `load_applications` rebinds a module-level global, which makes the code harder to follow and test. | Return the loaded dict and let the caller assign it. |
| 13 | Insecure random for IDs | Security | Bandit B311 | Low | 51 | `random.randint` is predictable, so application IDs can be guessed. | Use `secrets.randbelow` (or `secrets.token_hex`). |
| 14 | Subprocess with partial path | Security | Bandit B404, B603, B607; Pylint W1510 | Low | 6, 74 | Running `mail` by name depends on `PATH`. An `email` argument starting with `-` could be read as an option, and `check` isn't set. | Find the full path with `shutil.which`, put `--` before the recipient, check the email format, and set `check=True`. |
| 15 | Built-in name overwritten | Style | Pylint W0622 | Low | 34 | The local variable `sum` overwrites the built-in `sum()`. | Removed when the function is rewritten in #4. |
| 16 | Unused import | Style | Pylint W0611, Flake8 F401 | Low | 2 | `math` is imported but never used. | Remove the import (or use `math.isclose` if it's needed). |
| 17 | Non-snake_case function names | Convention | Pylint C0103 (×10) | Low | 14–81 | `calculateEMI`, `checkEligibility`, etc. don't follow PEP 8 naming. | Rename to `calculate_emi`, `check_eligibility`, … and update every call site. |
| 18 | Missing docstrings | Convention | Pylint C0114, C0116 (×12) | Low | 1, 14–93 | The module and its functions have no docstrings. | Add a module docstring and a one-line docstring to each function. |
| 19 | Too many arguments | Design | Pylint R0913, R0917 | Low | 20 | `check_eligibility` takes 6 positional arguments. | Removing the unused `history` parameter brings it down to 5. |
| 20 | Redundant `else` / `elif` after `return` | Style | Pylint R1705, R1703, R1714 | Low | 28–31, 82–91 | `if … return True else return False` is redundant, and the chained `==` checks should use `in`. | `return loan_type in ALLOWED_LOAN_TYPES`, and use plain `if` after each `return`. |
| 21 | f-string without placeholders | Style | Pylint W1309, Flake8 F541 | Low | 104 | `f"..."` has nothing to interpolate. | Use a plain string. |
| 22 | Superfluous parentheses | Style | Pylint C0325 | Low | 79 | `return (original - reduced)` has unnecessary parentheses. | Remove them. |
| 23 | Missing blank lines | Style | Flake8 E302 (×13), E305 | Low | 14–106 | Top-level functions need 2 blank lines before them. | Add 2 blank lines between top-level definitions. |
| 24 | Lines too long | Style | Flake8 E501 (×6), Pylint C0301 | Low | 20, 55, 70, 78, 95, 96, 100 | These lines are longer than 79 characters. | Wrap the arguments and split up the long `print` calls. |
| 25 | Code runs on import | Design | — | Low | 106 | `main()` runs whenever the module is imported. | Put it under `if __name__ == "__main__":`. |

## Demo output, before the fixes

```
EMI for 5L @ 9% for 5 years: 375000.000000001          <- #3
Eligible (score 760, income 15000, EMIs 12000): True    <- #2 (FOIR is 80%)
Eligible (unknown loan type 'crypto'): True             <- #2
Max loan for income 40000: 900000.0                     <- #4
Last schedule row: (12, 87.97, 0.0)
Risk band for 950: LOW                                  <- #8
Interest saved by prepaying 50000: 62275.065679061576   <- #5
Saved as: LN-87001346
Applications on file: 1
Upload to bureau skipped (no network)                   <- #21
```

## Commit plan

| Commit | Scope | Rows |
|--------|-------|------|
| 1 | Bandit (security) fixes | 1, 6, 10, 13, 14 |
| 2 | Pylint (quality + logic) fixes | 2–5, 7–9, 11, 12, 15–22, 25 |
| 3 | Flake8 (formatting) fixes | 23, 24 |
