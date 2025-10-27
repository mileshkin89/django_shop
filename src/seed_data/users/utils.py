import random

def get_random_phone_number() -> str:
    prefix = "+1"
    _phone_number = ""

    for i in range(10):
        digit = random.randint(0,9)
        _phone_number += str(digit)

    return prefix + _phone_number