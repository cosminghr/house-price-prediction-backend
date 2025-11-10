from app.entities.user import User


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
