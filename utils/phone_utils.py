import phonenumbers

def extract_and_format_numbers(text, country_code="+880"):
    seen = set()
    numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, None):
        number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        if number.startswith(country_code) and number not in seen:
            seen.add(number)
            numbers.append(number)
    return numbers