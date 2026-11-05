def clean_pan(pan):
    """
    Removes spaces from a PAN and upper-cases it.
    Assumes pan is a non-empty string.
    """
    return pan.strip().replace(' ', '').upper()

def parse_amount(text):
    """
    Converts an amount such as 'Rs 12,50,000' into an int.
    Assumes only digits remain after removing 'Rs', commas and spaces.
    """
    text = text.replace('Rs', '').replace(',', '').strip()
    return int(text)

def parse_tax_slab(line):
    """
    Parses 'LOW-HIGH:RATE' into a (low, high, rate) tuple.
    Assumes the line is always in that exact format.
    """
    limits, rate = line.split(':')
    low, high = limits.split('-')
    return int(low), int(high), int(rate)

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
