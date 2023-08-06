class FeatureError(Exception):
    pass

class FeatureDoesNotExist(FeatureError):
    pass

class FeatureValueMustBeBoolean(FeatureError):
    pass
