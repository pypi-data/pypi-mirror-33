class Adapter:
    """Adapter class to implement different
    feature flag config backends
    """
    def flags(self):
        """Must return a dict with valid flags and boolean values
        """
        return dict()

    def enable(self, name):
        """Enables a feature flag
        """
        pass

    def disable(self, name):
        """Disables a feature flag
        """
        pass

    def clean(self, flag_names):
        """Clean out legacy flags
        """
        pass
