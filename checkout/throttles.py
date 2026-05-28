from core.throttling import RedisTokenBucketThrottle


class CheckoutSTKPushThrottle(RedisTokenBucketThrottle):
    scope = "checkout_stk_push"

    def get_cache_ident(self, request, view):
        return f"{self.get_ident(request)}:{getattr(request.user, 'id', 'anonymous')}"
