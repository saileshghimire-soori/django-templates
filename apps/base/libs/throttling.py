from rest_framework.throttling import ScopedRateThrottle


class CustomScopedRateThrottle(ScopedRateThrottle):
    @property
    def throttle_scope(self):

        if self.request.user.is_superuser:
            return "superuser"

        method_scope_map = {
            "GET": "get",
            "POST": "post",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        scope_suffix = method_scope_map.get(self.request.method, "get")
        scope = (
            f"auth_{scope_suffix}"
            if self.request.user and self.request.user.is_authenticated
            else f"public_{scope_suffix}"
        )
        return scope

    def allow_request(self, request, view):
        self.request = request
        self.scope = self.throttle_scope
        # If adoes not have a `throttle_scope` always allow the request
        if not self.scope:
            return True

        # Determine the allowed request rate as we normally would during
        # the `__init__` call.
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

        # We can now proceed as normal.
        return self._allow_request(request, view)

    def _allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.

        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()
