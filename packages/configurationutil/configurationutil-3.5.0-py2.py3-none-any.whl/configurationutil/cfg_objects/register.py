# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from classutils import SingletonType
from classutils.decorators import class_cache_result, clear_class_cached_results
from .. import Configuration

logging = logging_helper.setup_logging()

# TODO: Write some basic unittests


class RegisterConfig(with_metaclass(SingletonType, object)):

    """ RegisterConfig registers and caches the config registration for APIConfig.

    This means register only has to be called once per config file (increases performance).

    """

    def __init__(self,
                 registrations):

        """

        :param registrations:   A dict containing the config registrations to be made
                                available on this object.
                                Example:
                                    {
                                        'dummy': {
                                            'config': 'dummy',
                                            'config_type': cfg_params.CONST.yaml,
                                            'template': '<path to dummy template>',
                                            'schema': '<path to dummy schema>'
                                        },
                                        'dummy2': {
                                            'config': 'dummy2',
                                            'config_type': cfg_params.CONST.yaml,
                                            'template': '<path to dummy2 template>',
                                            'schema': '<path to dummy2 schema>'
                                        }
                                    }
        """

        self._registrations = registrations

        # Retrieve configuration instance
        self._cfg = Configuration()

    @clear_class_cached_results
    def invalidate(self):
        """ Clears cached registrations.

        Call this is you want the register methods to be re-run.

        """
        pass

    @class_cache_result
    def _register(self,
                  registration):

        # Lookup registration
        registration_params = self._registrations[registration]

        # Register configuration
        self._cfg.register(**registration_params)

        return self._cfg

    def __getattr__(self, registration):

        # create dummy register function for registration
        def register_function():
            return self._register(registration)

        return register_function
