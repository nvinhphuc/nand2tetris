def is_number(str):
    for char in str:
        if (char < '0' or char > '9'): return False
    return True

def to_xml_text(str):
    if str == "<":
        return "&lt;"
    elif str == ">":
        return "&gt;"
    elif str == "&":
        return "&amp;"
    return str

if __name__ == "__main__":
    assert is_number("1231513451") == True
    assert is_number("123151345a") == False