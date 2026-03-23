import time
import logging

import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.config import WIKI_API_URL, RATE_LIMIT_SECONDS

logger = logging.getLogger(__name__)


class WikiClient:
    """MediaWiki API client with rate limiting and retries."""

    def __init__(self, api_url=None, rate_limit=None):
        self.api_url = api_url or WIKI_API_URL
        self.rate_limit = rate_limit if rate_limit is not None else RATE_LIMIT_SECONDS
        self._last_request_time = 0

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; TibiaWikiDownloader/1.0; Python/requests)",
        })

        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.verify = False

    def _rate_limit_wait(self):
        """Wait to respect rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def query(self, **params):
        """Make a query to the MediaWiki API.

        Args:
            **params: API parameters (action is set to 'query' automatically)

        Returns:
            dict: Parsed JSON response
        """
        params["action"] = "query"
        params["format"] = "json"

        self._rate_limit_wait()
        self._last_request_time = time.time()

        response = self.session.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()
