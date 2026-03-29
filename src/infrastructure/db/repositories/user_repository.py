from src.domain.interfaces.repositories import IUserRepository
from src.domain.entities import User
from src.domain.exceptions import UserNotFoundError

from src.infrastructure.db.models import User as UserModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class UserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def save(self, user: User) -> User:
        user_model = UserModel(
            email=user.email,
            hashed_password=user.hashed_password,
            google_id=user.google_id,
            is_active=user.is_active,
            is_verified=user.is_verified,
            balance=user.balance,
            role=user.role,
        )
        self._session.add(user_model)
        await self._session.commit()
        await self._session.refresh(user_model)
        return User.model_validate(user_model, from_attributes=True)

    async def get_by_id(self, user_id: str) -> User | None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = (await self._session.execute(query)).scalar_one_or_none()
        return User.model_validate(result, from_attributes=True) if result else None

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserModel).where(UserModel.email == email)
        result = (await self._session.execute(query)).scalar_one_or_none()
        return User.model_validate(result, from_attributes=True) if result else None

    async def get_by_google_id(self, user_google_id: str) -> User | None:
        query = select(UserModel).where(UserModel.google_id == user_google_id)
        result = (await self._session.execute(query)).scalar_one_or_none()
        return User.model_validate(result, from_attributes=True) if result else None

    async def update(self, user: User) -> User:
        query = select(UserModel).where(UserModel.id == user.id)
        user_model: UserModel | None = (
            await self._session.execute(query)
        ).scalar_one_or_none()
        if not user_model:
            raise UserNotFoundError()

        user_model.email = user.email
        user_model.hashed_password = user.hashed_password
        user_model.google_id = user.google_id
        user_model.is_active = user.is_active
        user_model.is_verified = user.is_verified
        user_model.balance = user.balance
        user_model.role = user.role

        await self._session.commit()
        await self._session.refresh(user_model)

        return User.model_validate(user_model, from_attributes=True)
