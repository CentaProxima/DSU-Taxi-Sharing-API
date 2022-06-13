import hashlib
from models.user import User

def pw_sha256(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest() if not password is None else None

def check_password(user_id, pw):
    password = User.query.with_entities(User.password).filter_by(id=user_id).first()
    if password and password[0] == pw_sha256(pw):
        return True
    return False