"""Loan eligibility and EMI calculator.

Calculates EMIs, checks loan eligibility, works out the maximum loan a
customer can afford, builds amortisation schedules, assigns risk bands,
estimates the interest saved by prepaying and stores application records
in a JSON file.

All interest rates are annual rates expressed as fractions (0.09 = 9%).
"""
import os
# Only the TLS-encrypted FTP_TLS client is used (see upload_to_bureau).
import ftplib  # nosec B402
import json
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime

MAX_FOIR = 0.5
MIN_AGE = 21
MAX_AGE = 60
CREDIT_SCORE_THRESHOLD = 750
INCOME_THRESHOLD = 25000
MIN_CREDIT_SCORE = 300
MAX_CREDIT_SCORE = 900
ALLOWED_LOAN_TYPES = frozenset({"home", "car", "personal"})
APPLICATIONS_FILE = "loans.json"
BUREAU_HOST = "ftp.creditbureau.example"
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
MAIL_FROM = os.environ.get("LOAN_MAIL_FROM", "loans@bank.example")


def calculate_emi(principal, annual_rate, years):
    """Return the monthly EMI; annual_rate is a fraction (0.09 = 9%)."""
    if not 0 <= annual_rate < 1:
        raise ValueError(
            "annual_rate must be a fraction between 0 and 1, "
            "e.g. 0.09 for 9%"
        )
    if years <= 0:
        raise ValueError("years must be positive")
    months = years * 12
    if annual_rate == 0:
        return principal / months
    monthly_rate = annual_rate / 12
    growth = (1 + monthly_rate) ** months
    return principal * monthly_rate * growth / (growth - 1)


def check_eligibility(age, income, credit_score, existing_emi, loan_type):
    """Return True if the applicant meets every eligibility rule."""
    if age < MIN_AGE or age > MAX_AGE:
        return False
    if income <= 0:
        return False
    if loan_type not in ALLOWED_LOAN_TYPES:
        return False
    if existing_emi / income > MAX_FOIR:
        return False
    return (credit_score > CREDIT_SCORE_THRESHOLD
            and income > INCOME_THRESHOLD)


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Return the largest principal whose EMI fits within the FOIR limit."""
    available = income * MAX_FOIR - existing_emi
    if available <= 0:
        return 0.0
    months = years * 12
    if annual_rate == 0:
        return available * months
    monthly_rate = annual_rate / 12
    return available * (1 - (1 + monthly_rate) ** -months) / monthly_rate


def amortisation_schedule(principal, annual_rate, years):
    """Return (month, interest, closing balance) rows for the loan."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance = balance - (emi - interest)
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows


def application_id():
    """Return a new, unpredictable application ID such as LN-12345678."""
    return "LN-" + str(10000000 + secrets.randbelow(90000000))


def save_application(records, name, amount, file=APPLICATIONS_FILE):
    """Add an application to records, save them all and return its ID."""
    app_id = application_id()
    records[app_id] = {
        "name": name,
        "amount": amount,
        "date": datetime.now().isoformat(),
    }
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)
    return app_id


def load_applications(file=APPLICATIONS_FILE):
    """Return the stored applications, or an empty dict if there are none."""
    try:
        with open(file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


def upload_to_bureau(report_path, user=None, password=None):
    """Upload a report to the credit bureau over TLS-encrypted FTP."""
    user = user or os.environ.get("BUREAU_USER")
    password = password or os.environ.get("BUREAU_PASSWORD")
    if not user or not password:
        raise RuntimeError("Set BUREAU_USER and BUREAU_PASSWORD to upload")
    ftp = ftplib.FTP_TLS(BUREAU_HOST)
    ftp.login(user, password)
    ftp.prot_p()
    with open(report_path, "rb") as report:
        ftp.storbinary("STOR " + os.path.basename(report_path), report)
    ftp.quit()


def notify_applicant(email, status):
    """Email the applicant their application status over STARTTLS."""
    msg = EmailMessage()
    msg["Subject"] = "Loan " + status
    msg["From"] = MAIL_FROM
    msg["To"] = email
    msg.set_content("Your loan application status: " + status)
    with smtplib.SMTP(SMTP_HOST) as smtp:
        smtp.starttls()
        smtp.send_message(msg)


def interest_saved(principal, annual_rate, years, prepayment):
    """Return the interest saved by prepaying part of the principal."""
    months = years * 12
    original = calculate_emi(principal, annual_rate, years) * months
    reduced = calculate_emi(principal - prepayment, annual_rate, years)
    return original - reduced * months - prepayment


def risk_band(credit_score):
    """Return the risk band for a credit score, or INVALID if out of range."""
    if not MIN_CREDIT_SCORE <= credit_score <= MAX_CREDIT_SCORE:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


def main():
    """Run a short demo of the calculator."""
    emi = calculate_emi(500000, 0.09, 5)
    print("EMI for 5L @ 9% for 5 years:", round(emi, 2))
    high_foir = check_eligibility(35, 15000, 760, 12000, "personal")
    print("Eligible (score 760, income 15000, EMIs 12000):", high_foir)
    crypto = check_eligibility(30, 80000, 650, 0, "crypto")
    print("Eligible (unknown loan type 'crypto'):", crypto)
    strong = check_eligibility(40, 60000, 780, 10000, "home")
    print("Eligible (score 780, income 60000, EMIs 10000, home):", strong)
    max_loan = max_loan_amount(40000, 5000, 0.09, 5)
    print("Max loan for income 40000:", round(max_loan, 2))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    saved = interest_saved(500000, 0.09, 5, 50000)
    print("Interest saved by prepaying 50000:", round(saved, 2))
    applications = load_applications()
    print("Saved as:", save_application(applications, "Anil", 500000))
    print("Applications on file:", len(load_applications()))
    print("Upload to bureau skipped (no network)")


if __name__ == "__main__":
    main()
