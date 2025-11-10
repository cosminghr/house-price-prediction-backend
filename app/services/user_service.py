from app.entities.user import User


def list_users(db):
    return db.query(User).all()


def get_user_by_id(db, user_id):
    return db.get(User, user_id)


def update_user(db, user_id, username=None):
    user = db.get(User, user_id)
    if not user:
        return None
    if username is not None:
        user.username = username
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db, user_id):
    user = db.get(User, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def delete_all_users(db):
    count = db.query(User).delete(synchronize_session=False)
    db.commit()
    return count
