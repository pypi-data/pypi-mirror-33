from apodeflags import features
from unittest.mock import patch, PropertyMock

def with_features(**flags):
    """Decorator to run unittests with a specified
    flag configuration
    """
    def with_features_decorator(func):
        def func_wrapper(self):
            with patch.object(
                features.Features,
                'available_flags',
                new_callable=PropertyMock
            ) as method:
                method.return_value = flags
                return func(self)
        return func_wrapper
    return with_features_decorator
