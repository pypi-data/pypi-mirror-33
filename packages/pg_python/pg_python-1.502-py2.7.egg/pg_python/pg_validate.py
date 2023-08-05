"""
This code checks if a user name
or a phone number is legit or not.
"""


blocked_nos = ["7894561230", "2468013579","0246813579", "7891237890"]


def is_phone_no_valid(number_string):
    if len(number_string) < 6:
        return False, "phone number too short"
    if len(number_string) > 15:
        return False, "phone number too long"
    if len(list(set(number_string))) < 4:
        # number of unique digits are too less
        return False, "phone number appears wrong"
    if "+" in number_string and len(list(set(number_string))) < 6:
        return False, "phone number appears wrong"
    for x in set(number_string):
        if x not in ['0','1','2','3','4','5','6','7','8','9','+',"-","/", " "]:
            return False, "Illegal characters in phone number"
    last_digit = None
    single_diff = 0
    for i in range(len(number_string)):
        x = number_string[i]
        if x not in ['0','1','2','3','4','5','6','7','8','9']:
            continue
        x = int(x)
        if last_digit is None:
            last_digit = x
            continue
        if abs(x - last_digit) < 2:
            single_diff += 1
        last_digit = int(x)
    if single_diff > len(number_string) - 4:
        return False, "phone number appears wrong"
    for number in blocked_nos:
        if number in number_string:
            return False, "phone number appears wrong"
    return True, "correct number"


def is_name_valid(name):
    if len(name) < 4:
        return False
    unique_chars = len(set(name.lower()))
    if unique_chars < 3:
        return False
    return True



if __name__ == "__main__":
    is_phone_no_valid("+91 7349250104")
