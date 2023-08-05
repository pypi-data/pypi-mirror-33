class TokenMixin(object):
    def is_active(self):
        # by default a token that doesn't contain an attribute called 'active'
        # it will be considered as active
        return getattr(self, "active", True)
