from passlib.context import CryptContext
from app.repositories.user_repository import get_user_by_username, create_user
from app.entities.user import User

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return password_context.hash(password)


def verify_password(password, hashed):
    return password_context.verify(password, hashed)


def register(db, username, password):
    if get_user_by_username(db, username) is not None:
        return None
    return create_user(db, username, hash_password(password))


def login(db, username, password):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def set_password_hash(db, user_id, password_hash):
    user = db.get(User, user_id)
    if not user:
        return None
    user.password_hash = password_hash
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def change_password(db, user_id, old_password, new_password):
    user = db.get(User, user_id)
    if not user:
        return None, "not_found"
    if not verify_password(old_password, user.password_hash):
        return None, "bad_old"
    new_hash = hash_password(new_password)
    updated = set_password_hash(db, user_id, new_hash)
    return updated, None


def admin_reset_password(db, user_id, new_password):
    user = db.get(User, user_id)
    if not user:
        return None
    new_hash = hash_password(new_password)
    return set_password_hash(db, user_id, new_hash)
