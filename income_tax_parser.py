import re

SLAB_PATTERN = re.compile(r"(\d+)-(\d+):(\d+)", re.ASCII)


def clean_pan(pan):
    """
    Removes all whitespace from a PAN and upper-cases it.
    Returns None if the input is not a string or is empty after cleaning.
    """
    if not isinstance(pan, str):
        return None

    cleaned = "".join(pan.split()).upper()
    if cleaned == "":
        return None

    return cleaned


def parse_amount(text):
    """
    Converts an amount such as 'Rs 12,50,000' into an int.
    Returns None if the input is not a string or is not a valid amount.
    """
    if not isinstance(text, str):
        return None

    cleaned = "".join(text.replace("Rs", "").replace(",", "").split())

    # isascii() rejects Unicode digits and superscripts that isdigit() accepts
    if not cleaned.isascii() or not cleaned.isdigit():
        return None

    try:
        return int(cleaned)
    except ValueError:  # e.g. digit string longer than Python's int limit
        return None


def parse_tax_slab(line):
    """
    Parses 'LOW-HIGH:RATE' into a (low, high, rate) tuple.
    Returns None if the input is not a string or not in that exact format.
    """
    if not isinstance(line, str):
        return None

    match = SLAB_PATTERN.fullmatch(line.strip())
    if match is None:
        return None

    try:
        low, high, rate = (int(g) for g in match.groups())
    except ValueError:
        return None

    return low, high, rate


def main():
    print("==== Running clean_pan ====")
    value = input("Enter a PAN (e.g. abcde 1234f): ")
    print("Cleaned PAN:", clean_pan(value))

    print("\n==== Running parse_amount ====")
    value = input("Enter an amount (e.g. Rs 12,50,000): ")
    print("Amount in rupees:", parse_amount(value))

    print("\n==== Running parse_tax_slab ====")
    value = input("Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): ")
    print("Tax slab (low, high, rate):", parse_tax_slab(value))


if __name__ == "__main__":
    main()