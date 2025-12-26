try:
    import bcrypt
    _HAVE_BCRYPT = True
except Exception:
    _HAVE_BCRYPT = False
import hashlib

def hash_password(password: str) -> str:
    if _HAVE_BCRYPT:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(password: str, hashed: str) -> bool:
    if _HAVE_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed