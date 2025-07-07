from src.infrasturcture.db.models.users import User as UserModel
from src.domain.entities.user import User
from src.domain.enums.user_role import UserRole

import datetime

user_model = UserModel(
    email="danil470yusopov@gmail.com",
    hashed_password="hashed_password",
    google_id=None,
    is_active=True,
    is_verified=True,
    balance=100.0,
    role=UserRole.user,
    created_at=datetime.datetime.now()
    )

print(User.model_validate(user_model, from_attributes=True))