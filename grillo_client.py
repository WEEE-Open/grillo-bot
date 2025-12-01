"""Grillo API client for interacting with the WEEE-Open/grillo API."""
from token import OP
import requests
from typing import Dict, List, Optional, Any
from config import config

class GrilloClient:
    """Client for interacting with the Grillo API."""

    def __init__(self, api_url: str = None, api_token: str = None, user: dict = None, user_id: str = None):
        """
        Initialize the Grillo API client.

        Args:
            api_url: Base URL for the Grillo API
            api_token: API token for authentication (get from grillo web UI)
            user_id: LDAP user ID to associate with API token requests
        """
        self.api_url = api_url or config.GRILLO_API_URL
        self.api_token = api_token or config.GRILLO_API_TOKEN
        self.session = requests.Session()
        self.user = user
        self.user_id = user.get('uid') if user else None
        if not user and user_id:
            self.user_id = user_id
            self.user = self.get_user_by_uid(user_id)
            if 'error' in self.user:
                raise ValueError(f"User with UID '{user_id}' not found.")

        # Set up headers for API token auth
        if self.api_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })


    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Grillo API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
        # print("RESPONSE: ", response.json())
        # response.raise_for_status()

        return response

    def is_admin(self) -> bool:
        return True if self.user and 'soviet' in self.user.get('groups') else False

    def get_ldap_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from LDAP (requires admin API token).

        Returns:
            List of user objects with id, username, name, etc.
        """
        return self._make_request("GET", "/users").json()

    def get_user_by_uid(self, user_id: str) -> Dict[str, Any]:
        """
        Get LDAP user by user ID (requires admin API token).

        Args:
            user_id: LDAP user ID

        Returns:
            User object
        """
        return self._make_request("GET", f"/user?uid={user_id}").json()

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get LDAP user by Telegram ID (requires admin API token).

        Args:
            telegram_id: Telegram user ID

        Returns:
            User object or None if not found
        """
        try:
            user = self._make_request("GET", f"/user?telegram_id={telegram_id}").json()
            return user
        except Exception:
            return None

    # Location endpoints
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations."""
        raise NotImplementedError("get_locations method not implemented yet.")

    def ring_location(self, location_id: str = "default") -> bool:
        """
        Ring the WEEETofono at a location to request entry.

        Args:
            location_id: Location ID or "default" for the default location

        Returns:
            True if successful
        """
        res = self._make_request("POST", f"/locations/{location_id}/ring")
        return res.json().get("success", False), res.json()

    # Audit (lab time tracking) endpoints
    def get_audits(self, date_string: Optional[str] = None, user: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit entries for a week.

        Args:
            date_string: ISO date string (defaults to current week)
            user: User ID to filter by
        """
        raise NotImplementedError("get_audits method not implemented yet.")

    def clockin(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Clock in to the lab.

        Args:
            location: Location ID (defaults to default location)
        """
        data = {"login": True, "user": self.user["id"]}
        if location:
            data["location"] = location

        res = self._make_request("POST", "/audits", json=data).json()

        if 'error' in res:
            if res['error'] == 'Must provide summary when switching location':
                raise ValueError("Already clocked in. Please clock out before switching locations.")

        return res

    def clockout(self, summary: str) -> Dict[str, Any]:
        """
        Clock out from the lab.

        Args:
            summary: Summary of work done during the session
        """
        data = {
            "logout": True,
            "summary": summary,
            "user": self.user["id"],
            "approved": self.is_admin()
        }
        res = self._make_request("PATCH", "/audits", json=data).json()
        if 'error' in res:
            if res['error'] == 'No active audit found for user':
                raise ValueError("No active session to clock out from.")

        return res[0] # Patch returns a list, but we only edit one at a time

    ### Location endpoints
    def get_location(self, location_id: str = "default") -> Dict[str, Any]:
        """
        Get details of a specific location.

        Args:
            location_id: Location ID or "default" for the default location

        Returns:
            Location object
        """
        res = self._make_request("GET", f"/locations/{location_id}").json()
        if 'error' in res:
            if res['error'] == 'Location not found':
                raise ValueError(f"Location '{location_id}' not found.")
        return res

    # Booking endpoints
    # def get_bookings(self) -> List[Dict[str, Any]]:
    #     """Get bookings for the current week."""
    #     return self._make_request("GET", "/bookings")

    # def create_booking(self, start_time: int, end_time: Optional[int] = None) -> Dict[str, Any]:
    #     """
    #     Create a new booking.

    #     Args:
    #         start_time: Unix timestamp for booking start
    #         end_time: Unix timestamp for booking end (optional)
    #     """
    #     data = {"startTime": start_time}
    #     if end_time:
    #         data["endTime"] = end_time

    #     return self._make_request("POST", "/bookings", json=data)

    # def delete_booking(self, booking_id: int) -> bool:
    #     """
    #     Delete a booking.

    #     Args:
    #         booking_id: ID of the booking to delete
    #     """
    #     try:
    #         self._make_request("DELETE", f"/bookings/{booking_id}")
    #         return True
    #     except Exception:
    #         return False

    # # Event endpoints
    # def get_events(self) -> List[Dict[str, Any]]:
    #     """Get all events."""
    #     return self._make_request("GET", "/events")

    # # Server configuration
    # def get_config(self) -> Dict[str, Any]:
    #     """Get server configuration."""
    #     return self._make_request("GET", "/config")

    # # Codes (for QR code entry)
    # def generate_code(self) -> Dict[str, str]:
    #     """
    #     Generate a one-time entry code.

    #     Returns:
    #         Dictionary with 'code' key
    #     """
    #     return self._make_request("POST", "/codes")


# Initialize Grillo API client with admin token for user management
api_admin_grillo = GrilloClient()

def get_user_client_by_telegram(telegram_id: int) -> GrilloClient:
    """
    Get a Grillo client for a specific Telegram user.
    Falls back to admin client with user_id if user is not mapped.

    Args:
        telegram_id: Telegram user ID

    Returns:
        GrilloClient instance
    """
    from user_mapper import user_mapper
    user_client = user_mapper.get_client_for_user(telegram_id)
    if user_client:
        return user_client

    # Fall back to plain admin client for read-only operations
    return api_admin_grillo
