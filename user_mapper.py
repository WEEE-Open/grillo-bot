"""User mapping between Telegram and Grillo/LDAP users."""
import json
import os
from typing import Optional, Dict
from grillo_client import GrilloClient


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
        self.sessions = {}  # Cache of telegram_id -> session_cookie

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
                if user:
                    ldap_username = user.get('uid')
                else:
                    return False

            self.mappings[telegram_id] = ldap_username
            self._save_mappings()

            # Clear cached session
            if telegram_id in self.sessions:
                del self.sessions[telegram_id]

            return True
        except Exception:
            return False

    def get_ldap_user(self, telegram_id: int) -> Optional[str]:
        """
        Get the LDAP username for a Telegram user.

        Args:
            telegram_id: Telegram user ID

        Returns:
            LDAP username or None if not mapped
        """
        return self.mappings.get(telegram_id)

    def get_client_for_user(self, telegram_id: int) -> Optional[GrilloClient]:
        """
        Get a GrilloClient with session auth for a specific Telegram user.

        Args:
            telegram_id: Telegram user ID

        Returns:
            GrilloClient instance with user session or None if user not mapped
        """
        ldap_user = self.get_ldap_user(telegram_id)
        if not ldap_user:
            return None

        # Check if we have a cached session
        if telegram_id in self.sessions:
            session_cookie = self.sessions[telegram_id]
        else:
            # Generate new session
            try:
                session_cookie = self.grillo.generate_session_for_user(ldap_user)
                if session_cookie:
                    self.sessions[telegram_id] = session_cookie
                else:
                    return None
            except Exception:
                return None

        # Create new client with session and user_id
        return GrilloClient(
            api_url=self.grillo.api_url,
            session_cookie=session_cookie,
            user_id=ldap_user
        )

    def is_user_mapped(self, telegram_id: int) -> bool:
        """Check if a Telegram user is mapped to an LDAP user."""
        return telegram_id in self.mappings

    def list_mappings(self) -> Dict[int, str]:
        """Get all user mappings."""
        return self.mappings.copy()
