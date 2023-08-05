import time

import requests


class SessionThrottler(object):
    def __init__(self, requests_per_second=20):
        self.last_response_start = None  # type: float
        self.requests_per_second = requests_per_second  # type: int
        self._backoff = 1.0 / self.requests_per_second  # type: float
        self._current_request = None
        super().__init__()

    def __str__(self):
        return 'Throttle: {:d} requests per second'.format(
            self.requests_per_second
        )

    def __repr__(self):
        return '<SessionThrottler: {:d}r/s>'.format(self.requests_per_second)

    @classmethod
    def register(cls, s: requests.Session, requests_per_second: int = 20):
        s.hooks['response'].append(cls(requests_per_second))

    def __call__(self, response: requests.Response, *args, **kwargs) -> None:
        """
        Hook for throttling requests (or really responses)

        :param response: Response object for the currently processed request
        :return: We always return nothing as we do not alter the response body
        """
        if self.last_response_start is None:
            self.last_response_start = requests.sessions.preferred_clock()
            return None

        now = requests.sessions.preferred_clock()
        elapsed = now - self.last_response_start
        if elapsed < self._backoff:
            time.sleep(self._backoff - elapsed)
            self.last_response_start = now + self._backoff - elapsed

        return None

