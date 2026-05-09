from app.core.security import hash_password
from app.db.session import SessionLocal
from app.db.repositories.user_repo import UserRepository

db = SessionLocal()
user_repo = UserRepository(db)
user = user_repo.get_by_email("test@email.com")
if user:
    user.password = hash_password("Yash@1234")
    db.commit()
    print("Password updated successfully.")
else:
    print("User not found.")
