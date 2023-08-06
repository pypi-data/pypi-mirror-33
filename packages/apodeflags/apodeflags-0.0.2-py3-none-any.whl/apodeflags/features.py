from . import errors, adapter

class Features:
    ADAPTER = adapter.Adapter
    AVAILABLE_FLAGS = dict(
        new_feature = False, # Test flag
    )

    @property
    def adapter(self):
        return self.ADAPTER()

    @property
    def available_flags(self):
        return self.AVAILABLE_FLAGS.copy()

    def is_enabled(self, name):
      return self.get(name) is True

    def is_disabled(self, name):
      return self.get(name) is False

    def enable(self, name):
        self.adapter.enable(name)

    def disable(self, name):
        self.adapter.disable(name)

    def get(self, name):
      try:
        return self.flag(name)
      except KeyError:
        raise errors.FeatureDoesNotExist

    def flag(self, name):
      if not hasattr(self, '_flags'):
          self._flags = self.available_flags
          self.adapter.clean(self.available_flags.keys())
          self._flags.update(self.adapter.flags())
          self.validate()

      return self._flags[name]

    def validate(self):
        # Only accept available flags
        invalid_flags = set(self._flags.keys()) - set(self.available_flags)
        if len(invalid_flags) > 0:
            raise errors.FeatureDoesNotExist(f"Invalid feature flags: {invalid_flags}")

        # Only accept True or False values
        invalid_values = set(self._flags.values()) - set([True, False])
        if len(invalid_values) > 0:
            raise errors.FeatureValueMustBeBoolean(f"Invalid feature flag values: {invalid_values}")
