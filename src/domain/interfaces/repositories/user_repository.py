from src.domain.entities import User

from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user in the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """Retrieve a user by their unique ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    async def get_by_google_id(self, user_google_id: str) -> User | None:
        """Retrieve a user by their Google ID."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user in the repository."""
        pass
