from ..utils.encryption import EncryptionManager
from ..db.repositories.social_accounts_repository import SocialAccountsRepository

import json


class CredentialsManager:
    def __init__(
        self,
        encryption_manager: EncryptionManager,
        social_accounts_repository: SocialAccountsRepository,
    ):
        self.encryption_manager = encryption_manager
        self.social_accounts_repository = social_accounts_repository

    def get_decrypted_credentials(self, user_id: str, platform: str) -> dict:
        social_account = self.social_accounts_repository.get_social_account(
            user_id, platform=platform
        )
        if not social_account:
            raise ValueError(
                f"No social account found for user_id={user_id} platform={platform}"
            )

        plaintext = self.encryption_manager.decrypt(
            wrapped_dek=social_account.wrapped_dek,
            ciphertext=social_account.encrypted_credentials,
        )

        return json.loads(plaintext.decode("utf-8"))


def get_credentials_manager(
    encryption_manager: EncryptionManager,
    social_accounts_repository: SocialAccountsRepository,
) -> CredentialsManager:
    return CredentialsManager(
        encryption_manager=encryption_manager,
        social_accounts_repository=social_accounts_repository,
    )
