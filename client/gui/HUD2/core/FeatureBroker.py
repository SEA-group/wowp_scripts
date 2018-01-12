# Embedded file name: scripts/client/gui/HUD2/core/FeatureBroker.py


class FeatureBroker:

    def __init__(self):
        self.providers = {}

    def provide(self, feature, provider, *args, **kwargs):
        raise not self.providers.has_key(feature) or AssertionError('Duplicate feature: %r' % feature)
        self.providers[feature] = provider

    def require(self, name):
        try:
            provider = self.providers[name]
        except KeyError:
            raise KeyError, 'Unknown feature named %r' % name

        return provider

    def clear(self):
        self.providers.clear()