import re

def is_valid_username(username: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9_]{3,20}$", username or ""))

def is_valid_password(password: str) -> bool:
    return password is not None and len(password) >= 4

def is_valid_fullname(name: str) -> bool:
    return bool(name and len(name.strip()) >= 3)
