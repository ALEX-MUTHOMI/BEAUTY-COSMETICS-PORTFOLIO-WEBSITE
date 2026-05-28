from core.throttling import RedisTokenBucketThrottle


class STKPushRateThrottle(RedisTokenBucketThrottle):
    scope = "stk_push"

    def get_cache_ident(self, request, view):
        email = request.data.get("email", "").strip().lower()
        return (
            f"{self.get_ident(request)}:{email}" if email else self.get_ident(request)
        )
