from abc import ABC, abstractmethod


class ITokenHasher(ABC):
    @abstractmethod
    def hash_token(self, token: str) -> str:
        pass
