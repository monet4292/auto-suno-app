"""
Suno API Client
Handles all API interactions with Suno.com

Part of Clean Architecture refactor from legacy_modules/suno_batch_download.py
"""
import time
import requests
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

from src.utils.logger import logger


class SunoApiClient:
    """
    API Client for Suno.com interactions

    Handles:
    - Profile clips fetching with pagination
    - User information retrieval
    - Clip fetching by UUIDs
    - Rate limiting and proxy management
    - Session token authentication
    """

    def __init__(self, session_token: Optional[str] = None, proxy_list: Optional[List[str]] = None):
        """
        Initialize Suno API Client

        Args:
            session_token: JWT token from browser cookies (__session)
            proxy_list: List of proxy URLs for requests
        """
        self.session_token = session_token
        self.proxy_list = proxy_list or []
        self.base_url = "https://studio-api.prod.suno.com/api"

        # Setup headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        if self.session_token:
            self.headers['Authorization'] = f'Bearer {self.session_token}'

        # Rate limiting state
        self._last_request_time = 0
        self._rate_limit_wait = 10

    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the proxy list"""
        if not self.proxy_list:
            return None
        proxy_url = self.proxy_list[len(self.proxy_list) % len(self.proxy_list)]  # Simple rotation
        return {'http': proxy_url, 'https': proxy_url}

    def _handle_rate_limit(self, response: requests.Response) -> bool:
        """
        Handle rate limiting from API responses

        Args:
            response: The HTTP response

        Returns:
            True if rate limited and should retry, False otherwise
        """
        if response.status_code == 429:
            logger.warning(f"Rate limit hit (429), waiting {self._rate_limit_wait}s...")
            time.sleep(self._rate_limit_wait)
            self._rate_limit_wait = min(self._rate_limit_wait + 5, 60)  # Exponential backoff
            return True

        # Reset rate limit wait on successful request
        if response.status_code == 200:
            self._rate_limit_wait = 10

        return False

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request with error handling and rate limiting

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional requests parameters

        Returns:
            JSON response data or None if failed
        """
        url = f"{self.base_url}{endpoint}"

        # Add proxies if available
        if 'proxies' not in kwargs:
            kwargs['proxies'] = self._get_random_proxy()

        # Add default timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30

        # Add headers
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers

        try:
            # Rate limiting: ensure minimum delay between requests
            elapsed = time.time() - self._last_request_time
            if elapsed < 2:  # Minimum 2 seconds between requests
                time.sleep(2 - elapsed)

            response = requests.request(method, url, **kwargs)
            self._last_request_time = time.time()

            # Handle rate limiting
            if self._handle_rate_limit(response):
                # Retry once after rate limit
                response = requests.request(method, url, **kwargs)
                self._last_request_time = time.time()

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {endpoint} - {str(e)}")
            return None

    def fetch_profile_clips(self, profile_name: str, start_page: int = 0,
                           max_pages: Optional[int] = None) -> Tuple[List[Dict], int, bool]:
        """
        Fetch clips from a user profile with pagination

        Args:
            profile_name: Profile name (with or without @)
            start_page: Starting page number (0-indexed)
            max_pages: Maximum pages to fetch (None for unlimited)

        Returns:
            Tuple of (clips_list, last_page_fetched, has_more_pages)
        """
        logger.info(f"Fetching clips from profile: {profile_name} (starting page {start_page})")

        # Remove @ prefix if present
        if profile_name.startswith('@'):
            profile_name = profile_name[1:]

        endpoint = f"/profiles/{profile_name}/clips"
        all_clips = []
        page = start_page
        pages_fetched = 0

        while True:
            # Check page limit
            if max_pages and pages_fetched >= max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                return all_clips, page - 1, True

            params = {'page': page}
            data = self._make_request('GET', endpoint, params=params)

            if not data:
                logger.error(f"Failed to fetch page {page}")
                return all_clips, page - 1, False

            clips = data.get('clips', [])
            if not clips:
                logger.info(f"No more clips found at page {page}")
                return all_clips, page - 1, False

            all_clips.extend(clips)
            logger.info(f"Page {page}: {len(clips)} clips")
            page += 1
            pages_fetched += 1

            # Delay between pages
            if pages_fetched < (max_pages or float('inf')):
                time.sleep(5)

        return all_clips, page - 1, False

    def fetch_my_clips(self) -> List[Dict]:
        """
        Fetch current user's clips from /feed/v2

        Returns:
            List of clip dictionaries
        """
        logger.info("Fetching current user's clips from /feed/v2")

        endpoint = "/feed/v2"
        params = {'page': 0}

        data = self._make_request('GET', endpoint, params=params)

        if not data:
            logger.error("Failed to fetch user clips")
            return []

        clips = data.get('clips', [])
        logger.info(f"Found {len(clips)} user clips from /feed/v2")
        return clips

    def fetch_create_clips(self) -> List[Dict]:
        """
        Fetch current user's clips from /feed/v2 (accessed via /create page)
        This is the same endpoint as fetch_my_clips but accessed from /create context

        Returns:
            List of clip dictionaries
        """
        # Backwards-compatible single-page fetch (kept for callers that expect a simple list)
        logger.info("Fetching clips from /create page context (using /feed/v2) - single page")

        endpoint = "/feed/v2"
        params = {'page': 0}

        data = self._make_request('GET', endpoint, params=params)

        if not data:
            logger.error("Failed to fetch clips from /create context")
            return []

        clips = data.get('clips', [])
        logger.info(f"Found {len(clips)} clips from /create context (page 0)")
        return clips

    def fetch_create_clips_paginated(self, start_page: int = 0, max_pages: Optional[int] = None) -> Tuple[List[Dict], int, bool]:
        """
        Fetch current user's clips from the feed endpoint used by /create with pagination.

        Args:
            start_page: starting page (0-indexed)
            max_pages: maximum pages to fetch (None = fetch until empty)

        Returns:
            (all_clips, last_page_fetched, has_more_pages)
        """
        logger.info(f"Fetching clips from /create context with pagination (starting page {start_page})")

        endpoint = "/feed/v2"
        all_clips: List[Dict] = []
        page = start_page
        pages_fetched = 0

        while True:
            if max_pages and pages_fetched >= max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                return all_clips, page - 1, True

            params = {'page': page}
            data = self._make_request('GET', endpoint, params=params)

            if not data:
                logger.error(f"Failed to fetch /feed/v2 page {page}")
                return all_clips, page - 1, False

            clips = data.get('clips', [])
            if not clips:
                logger.info(f"No more clips found at /feed/v2 page {page}")
                return all_clips, page - 1, False

            all_clips.extend(clips)
            logger.info(f"/feed/v2 Page {page}: {len(clips)} clips")
            page += 1
            pages_fetched += 1

            # polite delay between pages
            if pages_fetched < (max_pages or float('inf')):
                time.sleep(2)

        return all_clips, page - 1, False

    def get_current_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information

        Returns:
            User info dict with username, email, credits, etc.
        """
        logger.info("Fetching current user information")

        endpoint = "/billing/info"
        data = self._make_request('GET', endpoint)

        if not data:
            logger.error("Failed to fetch user info")
            return None

        user_info = {
            'username': data.get('display_name', ''),
            'email': data.get('email', ''),
            'credits': data.get('total_credits_left', 0)
        }

        logger.info(f"User: @{user_info['username']}, Credits: {user_info['credits']}")
        return user_info

    def fetch_clips_by_uuids(self, uuids: List[str]) -> List[Dict]:
        """
        Fetch clip information by UUIDs

        Args:
            uuids: List of clip UUIDs

        Returns:
            List of clip dictionaries
        """
        logger.info(f"Fetching {len(uuids)} clips by UUID")

        clips = []

        for idx, uuid in enumerate(uuids, 1):
            endpoint = f"/clips/{uuid}"
            data = self._make_request('GET', endpoint)

            if data:
                clips.append(data)
                logger.info(f"[{idx}/{len(uuids)}] {data.get('title', 'Unknown')}")
            else:
                logger.error(f"Failed to fetch clip {uuid}")

            # Delay between requests
            if idx < len(uuids):
                time.sleep(2)

        return clips

    def update_session_token(self, token: str):
        """
        Update the session token for authentication

        Args:
            token: New JWT session token
        """
        self.session_token = token
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        else:
            self.headers.pop('Authorization', None)

    def set_proxy_list(self, proxy_list: List[str]):
        """
        Update the proxy list

        Args:
            proxy_list: New list of proxy URLs
        """
        self.proxy_list = proxy_list or []