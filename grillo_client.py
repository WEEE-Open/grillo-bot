"""Grillo API client for interacting with the WEEE-Open/grillo API."""
from token import OP
import requests
from typing import Dict, List, Optional, Any
from config import config

class GrilloClient:
    """Client for interacting with the Grillo API."""

    def __init__(self, api_url: str = None, api_token: str = None, session_cookie: str = None, user: dict = None):
        """
        Initialize the Grillo API client.

        Args:
            api_url: Base URL for the Grillo API
            api_token: API token for authentication (get from grillo web UI)
            session_cookie: Session cookie for user-specific operations
            user_id: LDAP user ID to associate with API token requests
        """
        self.api_url = api_url or config.GRILLO_API_URL
        self.api_token = api_token or config.GRILLO_API_TOKEN
        self.session_cookie = session_cookie
        self.user = user
        self.user_id = user.get('uid') if user else None
        self.session = requests.Session()
        print("INITIALIZING GRILLO CLIENT for user: ", self.user)
        # Set up headers for API token auth
        if self.api_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })

        # Set up session cookie if provided
        if self.session_cookie:
            self.session.cookies.set("session", self.session_cookie)

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
        # If using API token and user_id is set, add uid to query params
        if self.api_token and self.user_id and not self.session_cookie:
            params = kwargs.get('params', {})
            if isinstance(params, dict):
                params['uid'] = self.user_id
                kwargs['params'] = params

        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
        response.raise_for_status()

        if response.status_code == 204:  # No content
            return {}

        return response.json()

    def is_admin(self) -> bool:
        raise NotImplementedError("is_admin method not implemented yet.")

    def get_ldap_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from LDAP (requires admin API token).

        Returns:
            List of user objects with id, username, name, etc.
        """
        return self._make_request("GET", "/users")

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get LDAP user by Telegram ID (requires admin API token).

        Args:
            telegram_id: Telegram user ID

        Returns:
            User object or None if not found
        """
        try:
            user = self._make_request("GET", f"/user?telegram_id={telegram_id}")
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
        raise NotImplementedError("ring_location method not implemented yet.")

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

        return self._make_request("POST", "/audits", json=data)

    def clockout(self, summary: str) -> Dict[str, Any]:
        """
        Clock out from the lab.

        Args:
            summary: Summary of work done during the session
        """
        data = {
            "logout": True,
            "summary": summary
        }
        return self._make_request("PATCH", "/audits", json=data)

    ### Location endpoints
    def get_location(self, location_id: str = "default") -> Dict[str, Any]:
        """
        Get details of a specific location.

        Args:
            location_id: Location ID or "default" for the default location

        Returns:
            Location object
        """
        return self._make_request("GET", f"/locations/{location_id}")

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
