"""User mapping between Telegram and Grillo/LDAP users."""
import json
import os
from typing import Optional, Dict
from grillo_client import GrilloClient, api_admin_grillo


class UserMapper:
    """Map Telegram users to Grillo/LDAP users and manage sessions."""

    def __init__(self, grillo_client: GrilloClient, mapping_file: str = "user_mapping.json"):
        """
        Initialize the user mapper.

        Args:
            grillo_client: GrilloClient instance with admin API token
            mapping_file: Path to JSON file storing Telegram ID to LDAP ID mappings
        """
        self.grillo = grillo_client
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()
        self.clients = {}  # Cache of telegram_id -> GrilloClient

    def _load_mappings(self) -> Dict[int, str]:
        """Load user mappings from file."""
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r') as f:
                # Convert string keys back to ints
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        return {}

    def _save_mappings(self):
        """Save user mappings to file."""
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mappings, f, indent=2)

    def map_user(self, telegram_id: int, ldap_username: str = None) -> bool:
        """
        Map a Telegram user to an LDAP user. If ldap_username is not provided,
        attempts to auto-discover the user via Telegram ID.

        Args:
            telegram_id: Telegram user ID
            ldap_username: Optional LDAP username (for manual mapping)

        Returns:
            True if mapping was successful
        """
        try:
            # If username not provided, try to find user by Telegram ID
            if not ldap_username:
                user = self.grillo.get_user_by_telegram_id(telegram_id)
                print("AUTO-DISCOVERED USER:")
                print(user)
                # if user:
                #     ldap_username = user.get('uid')
                if not user:
                    return False

            self.mappings[telegram_id] = user
            self._save_mappings()

            # Clear cached session
            if telegram_id in self.sessions:
                del self.sessions[telegram_id]

            return True
        except Exception:
            return False

    def get_client_for_user(self, telegram_id: int) -> Optional[GrilloClient]:
        """
        Get a GrilloClient with session auth for a specific Telegram user.

        Args:
            telegram_id: Telegram user ID

        Returns:
            GrilloClient instance with user session or None if user not mapped
        """
        user = self.mappings.get(telegram_id)
        if not user:
            res = self.map_user(telegram_id)
            if not res:
                return None

        # Check if we have a cached client
        if telegram_id in self.clients:
            client = self.clients[telegram_id]
        else:
            client = GrilloClient(
                api_url=self.grillo.api_url,
                user=user
            )
            self.clients[telegram_id] = client

        return client

    def is_user_mapped(self, telegram_id: int) -> bool:
        """Check if a Telegram user is mapped to an LDAP user."""
        return telegram_id in self.mappings

    def list_mappings(self) -> Dict[int, str]:
        """Get all user mappings."""
        return self.mappings.copy()

# Initialize user mapper
user_mapper = UserMapper(api_admin_grillo)