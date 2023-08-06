# encoding: utf-8

import os
import re
import shutil
import logging_helper
from copy import deepcopy
from appdirs import AppDirs
from tempfile import mkdtemp
from past.builtins import cmp
from future.builtins import str as newstr
from future.utils import with_metaclass, lmap
from classutils.singleton import SingletonType
from fdutil.path_tools import pop_path, ensure_path_exists
from jsonschema import SchemaError, ValidationError, Draft4Validator
from configurationutil.cfg_providers.json_provider import JSONConfig
from configurationutil.cfg_providers.yaml_provider import YAMLConfig
from configurationutil.cfg_providers.commented_yaml_provider import CommentedYAMLConfig

logging = logging_helper.setup_logging()

# App details
APP_NAME = None  # Once Configuration is initialised changes to this parameter will be ignored!
APP_AUTHOR = None  # Once Configuration is initialised changes to this parameter will be ignored!
APP_VERSION = None  # Once Configuration is initialised changes to this parameter will be ignored!

CACHE_FOLDER = u'cache'
LOGS_FOLDER = u'logs'
PLUGIN_FOLDER = u'plugins'

VERSION_IGNORE_LIST = [
    CACHE_FOLDER,
    LOGS_FOLDER,
    PLUGIN_FOLDER
]

DEV_FORCE_REWRITE_CONFIG = False
DEV_FORCE_REWRITE_CONFIG_DENY = []


# Export constants
class _CONST:

    def __init__(self): pass

    # Master config properties
    @property
    def master_template(self): return u'master_config_template.json'

    @property
    def master_schema(self): return u'master_config_schema.json'

    @property
    def master_fn(self): return u'master_config.json'

    @property
    def master_registered(self): return u'registered_cfg'

    # Config Keys
    @property
    def cfg_dir(self): return u'config'

    @property
    def cfg_schema(self): return u'schema'

    @property
    def cfg_template(self): return u'template'

    @property
    def cfg_src_schema(self): return u'src_schema'

    @property
    def cfg_src_template(self): return u'src_template'

    @property
    def cfg_fn(self): return u'filename'

    @property
    def cfg_type(self): return u'type'

    # Available Config types
    @property
    def json(self): return u'json'

    @property
    def yaml(self): return u'yaml'

    @property
    def commented_yaml(self): return u'commented_yaml'


CONST = _CONST()  # Initialise Constants


# Config Types
CFG_TYPE_CLASS = u'class'
CFG_TYPE_EXT = u'ext'

CFG_TYPES = {
    CONST.json: {
        CFG_TYPE_CLASS: JSONConfig,
        CFG_TYPE_EXT: u'json'
    },
    CONST.yaml: {
        CFG_TYPE_CLASS: YAMLConfig,
        CFG_TYPE_EXT: u'yaml'
    },
    CONST.commented_yaml: {
        CFG_TYPE_CLASS: CommentedYAMLConfig,
        CFG_TYPE_EXT: u'yaml'
    }
}

TEMPLATE_DEFAULTS_ITEM = u'_DEFAULTS'

# Schema Types
SCHEMA_TYPES = {
    # string was originally unicode, tried newstr but that causes Yaml cannot handle that so falling back to str!
    u'string': str,
    u'number': float,
    u'object': dict,
    u'array': list,
    u'boolean': bool,
    u'null': None
}


class Configuration(with_metaclass(SingletonType, object)):

    def __init__(self,
                 preload=False):

        """ Initialise Config class

            APP_NAME Must be set before initialisation.
            APP_AUTHOR is optional
            APP_VERSION is optional

            :param preload: Set True to preload all config objects
        """

        logging.info(u'Initialising configuration...')

        # Initialisation fails if APP_NAME has not been configured!
        if APP_NAME is None:
            raise ValueError(u'Cannot initialise configuration: APP_NAME not defined.')

        # Prepare app_dirs so we can setup paths
        self.__app_kwargs = {
            u'appname': APP_NAME
        }

        if APP_AUTHOR is not None:
            self.__app_kwargs[u'appauthor'] = APP_AUTHOR

        # Get reference to version agnostic paths for version checking
        self.__app_dirs_all_versions = AppDirs(**self.__app_kwargs)

        # Set version agnostic paths
        self.__basic_app_dirs = AppDirs(**self.__app_kwargs)

        if APP_VERSION is not None:
            normalised_version = self.normalise_version(APP_VERSION)

            if not self.validate_version(normalised_version):
                raise ValueError(u'Version is Invalid: {v}'.format(v=APP_VERSION))

            self.__app_kwargs[u'version'] = normalised_version

        # Set paths to users OS default locations.
        self.__app_dirs = AppDirs(**self.__app_kwargs)

        logging.info(u'Config file path: {p}'.format(p=self.config_path))
        logging.debug(u'Config schema path: {p}'.format(p=self.schema_path))
        logging.debug(u'Config template path: {p}'.format(p=self.template_path))
        logging.debug(u'Cache path: {p}'.format(p=self.cache_path))
        logging.info(u'Data path: {p}'.format(p=self.data_path))
        logging.info(u'Log path: {p}'.format(p=self.log_path))

        # Set temp path
        self.__temp_path = mkdtemp(prefix=u'{app_name}_Temp_'.format(app_name=APP_NAME))
        logging.info(u'Temp path: {p}'.format(p=self.temp_path))

        # Set the master config path.  Any config required for this class to work will be stored here.
        self.__master_cfg_file = os.path.join(self.config_path, u'master_config.json')

        # Load the master config schema
        self.__master_cfg_schema_file = os.path.join(pop_path(__file__), CONST.master_schema)
        self.__master_cfg_schema_obj = self.__get_schema_obj(self.__master_cfg_schema_file)

        # Initialise master config
        self.__master_cfg = self.__init_cfg(config_file=self.__master_cfg_file,
                                            config_type=CONST.json,
                                            template=os.path.join(pop_path(__file__), CONST.master_template),
                                            schema=self.__master_cfg_schema_file)

        # Keep reference to registered configurations
        self.__registered_cfg = self.__master_cfg.cfg.get(u'registered_cfg')  # Keep a record of all registered config.
        self.__registered_cfg_objs = {}  # Keeping this record separate as they should not be dumped into config files.

        # If preload is set attempt to preload each registered config.
        if preload:
            for cfg in self.__registered_cfg:
                try:
                    self.__load_cfg(config=cfg)

                except (SchemaError, ValidationError) as err:
                    logging.warning(u'Failed pre-loading {cfg}: {err}'.format(cfg=cfg,
                                                                              err=err))

        logging.info(u'Configuration initialised.')

    def __init_cfg(self,
                   config_file,
                   config_type,
                   template=None,
                   schema=None):

        """ Initialise the config file

        If this is the first run the config will be created (either blank, from template or from previous config),
        otherwise, it will be loaded.

        :param config_file: Path to config file being created / loaded
        :param config_type: Config type from types available in CFG_TYPES.
        :param template:    Path to template file
        :param schema:      Path to schema file
        """

        cfg_type = CFG_TYPES.get(config_type)
        cfg_class = cfg_type.get(CFG_TYPE_CLASS)

        new = False if os.path.exists(config_file) else True

        cfg_obj = cfg_class(config_file=config_file,
                            create=True)

        if new:
            # initialise from a template (this is done whether template is set or not as there should be a default
            # template provided with the config class being initialised)
            self.__init_from_template(cfg_obj=cfg_obj,
                                      config_type=config_type,
                                      template=template,
                                      schema=schema)

        # If a schema is specified make sure the cfg_obj is valid before returning
        # If the schema is invlaid this raises SchemaError.
        # If cfg_obj is invalid this raises ValidationError.
        if schema is not None:
            self.__validate_config(schema, cfg_obj)

        return cfg_obj

    def _load_template(self,
                       config_type,
                       template=None,
                       schema=None):

        """ Load the template configuration object

        :param config_type: Config type from types available in CFG_TYPES.
        :param template:    Path to template file
        :param schema:      Path to schema file
        """

        cfg_type = self._load_and_validate_config_type(config_type)
        cfg_class = cfg_type.get(CFG_TYPE_CLASS)

        # Load template
        cfg_template_obj = cfg_class(config_file=template if template is not None else cfg_class.DEFAULT_TEMPLATE)

        # Validate & apply template
        try:
            if schema is not None:
                self.__validate_config(schema, cfg_template_obj)

        except SchemaError as err:
            logging.error(u'Invalid schema for config template: {err}'.format(err=err))
            cfg_template_obj = None

        except ValidationError as err:
            logging.error(u'Template configuration is invalid: {err}'.format(err=err))
            cfg_template_obj = None

        return cfg_template_obj

    def __init_from_template(self,
                             cfg_obj,
                             config_type,
                             template=None,
                             schema=None):

        """ Initialise the configuration object from provided template

        :param cfg_obj:     Config object to initialise
        :param config_type: Config type from types available in CFG_TYPES.
        :param template:    Path to template file
        :param schema:      Path to schema file
        """

        cfg_template_obj = self._load_template(config_type=config_type,
                                               template=template,
                                               schema=schema)

        if cfg_template_obj is not None:
            # This will only apply the config if the template has a valid schema where provided
            cfg_obj.cfg = cfg_template_obj.cfg

            # Do not save the templates defaults item into config!
            if TEMPLATE_DEFAULTS_ITEM in cfg_obj.cfg:
                del cfg_obj.cfg[TEMPLATE_DEFAULTS_ITEM]

            cfg_obj.save()

        return cfg_template_obj

    def __load_cfg(self,
                   config):

        """ Load config file

        :param config: The name of the config to load.
        """

        if self.check_registration(config=config):
            cfg = self.__registered_cfg.get(config)

            cfg_type = CFG_TYPES.get(cfg.get(CONST.cfg_type))
            cfg_class = cfg_type.get(CFG_TYPE_CLASS)

            try:
                cfg_obj = cfg_class(config_file=os.path.join(self.config_path, cfg.get(CONST.cfg_fn)))

            except IOError:
                cfg_obj = self.__init_cfg(config_file=os.path.join(self.config_path, cfg.get(CONST.cfg_fn)),
                                          config_type=cfg.get(CONST.cfg_type),
                                          template=cfg.get(CONST.cfg_template),
                                          schema=cfg.get(CONST.cfg_schema))

            self.__validate_registered_config(config=config,
                                              obj=cfg_obj)

        else:
            raise KeyError(u'Cannot load config: {cfg}; Config not registered.'.format(cfg=config))

        self.__registered_cfg_objs[config] = cfg_obj

    def __reload_cfg(self,
                     config):

        """ Reload config file

        :param config: The name of the config to reload.
        """
        if self.check_registration(config):
            # Remove object if loaded
            if self.__check_loaded(config):
                del self.__registered_cfg_objs[config]

            # Load the config
            self.__load_cfg(config)

        else:
            raise KeyError(u'Cannot reload config: {cfg}; Config not registered.'.format(cfg=config))

    def register(self,
                 config,
                 config_type,
                 template=None,
                 schema=None,
                 upgradable=True,
                 upgrade_merge_template=False):

        """ Register a config file.

        :param config:                  The name of the config item being registered.  This will also be the filename.
        :param config_type:             The type of file this config item will be.
        :param template:                Template file to initialise config from.
        :param schema:                  Schema file, conforming to the JSON schema format, to validate config with.
        :param upgradable:              If True the config will attempt upgrade from previous version before creating
                                        from template.
                                        If False the config will always reload from template. (default=True)
        :param upgrade_merge_template:  If True then the template will be merged with the previous config at upgrade.
                                        If False then the template will only be used to initialise missing parameters.
                                        default=False.  This param is ignored if upgradable is False.
        """

        if DEV_FORCE_REWRITE_CONFIG:
            if config not in DEV_FORCE_REWRITE_CONFIG_DENY:
                logging.warning(u'Dev force re-write: {cfg}'.format(cfg=config))
                self.unregister(config=config)
                DEV_FORCE_REWRITE_CONFIG_DENY.append(config)

        # Try upgrade first if allowed
        if upgradable:
            self.__upgrade_cfg(config,
                               config_type=config_type,
                               template=template,
                               schema=schema,
                               upgrade_merge_template=upgrade_merge_template)

        if not self.check_registration(config):
            registration = self._create_basic_registration(config, config_type)

            self.__init_cfg(config_file=os.path.join(self.config_path,
                                                     registration[CONST.cfg_fn]),
                            config_type=config_type,
                            template=template,
                            schema=schema)

            self.__registered_cfg[config] = registration

            # TODO: Validate schema & template before creating / registering any files!
            # Currently if a validation error is raised during registration a default file is created that has to be
            # manually removed before a valid file can be created!
            if template is not None:
                cfg_type = self._load_and_validate_config_type(config_type)
                self.__register_template(config,
                                         template,
                                         cfg_type.get(CFG_TYPE_EXT))

            if schema is not None:
                self.__register_schema(config, schema)

            self.__validate_master_config()  # if invalid this raises either SchemaError or ValidationError.
            self.__master_cfg.save()

            logging.info(u'Configuration registered: {cfg}'.format(cfg=config))

        # else:
        #     logging.debug(u'Configuration already registered: {cfg}'.format(cfg=config))

    @staticmethod
    def _create_basic_registration(config,
                                   config_type):

        cfg_type = Configuration._load_and_validate_config_type(config_type)

        cfg_filename = u'{c}.{ext}'.format(c=config,
                                           ext=cfg_type.get(CFG_TYPE_EXT))

        registration = {
            CONST.cfg_fn: cfg_filename,
            CONST.cfg_type: config_type
        }

        return registration

    @staticmethod
    def _load_and_validate_config_type(config_type):

        cfg_type = CFG_TYPES.get(config_type)

        if cfg_type is None:
            raise LookupError(u'Config Type not found: {c}'.format(c=config_type))

        return cfg_type

    def unregister(self,
                   config):

        """ Unregister a config file.  This will also delete the config file.

        :param config:  The name of the config item being unregistered.
        """

        if self.check_registration(config):

            # Get paths & remove the config file
            paths = [
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_fn),
                    u'pth': self.config_path
                },
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_template),
                    u'pth': self.template_path
                },
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_schema),
                    u'pth': self.schema_path
                }
            ]

            for pth in paths:
                if pth.get(u'fn') is not None:
                    os.remove(os.path.join(pth[u'pth'], pth[u'fn']))

            # Remove registration
            del self.__registered_cfg[config]
            self.__master_cfg.save()

            # Remove object if loaded
            if self.__check_loaded(config):
                del self.__registered_cfg_objs[config]

            logging.info(u'Configuration unregistered: {cfg}'.format(cfg=config))

        else:
            logging.debug(u'Configuration does not exist: {cfg}'.format(cfg=config))

    def check_registration(self, config):

        """ Check whether config is already registered.

        :param config:  The name of the config item being checked.
        :return: boolean.  True if already registered.
        """

        return True if config in self.__registered_cfg.keys() else False

    def _check_upgradable(self,
                          config):

        """ Check whether config is upgradable.

        :return: (tuple) -> (upgradable, previous_version, previous_registration)
                    upgradable (boolean).           True if config can be upgraded otherwise False.
                    previous_version (float).       Version number for the latest version registered (not including
                                                    current). None if there are no previous versions.
                    previous_registration (obj)     Previous version of this config.
        """

        # Setup return values
        upgradable = False
        previous_version = self.last_version
        previous_registration = None

        # Check if we have the config registered.  If yes assume already upgraded.
        if not self.check_registration(config):
            # Check for previous config version.
            if self.last_version is not None:
                # load previous master config
                master_cfg_type = CFG_TYPES.get(CONST.json)
                master_cfg_class = master_cfg_type.get(CFG_TYPE_CLASS)
                old_master_path = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                               previous_version, CONST.cfg_dir, CONST.master_fn)

                old_master = master_cfg_class(config_file=old_master_path)

                # Try and get the config from our previous master
                previous_registration = old_master[CONST.master_registered].get(config)

                if previous_registration is not None:
                    upgradable = True

        return upgradable, previous_version, previous_registration

    def __upgrade_cfg(self,
                      config,
                      config_type,
                      template=None,
                      schema=None,
                      upgrade_merge_template=False):

        """ Upgrade a config file

        :param config:                  The name of the config item being upgraded.  This will also be the filename.
        :param config_type:             The type of file this config item will be.
        :param template:                Template file to initialise parameters from if not present in previous config.
        :param schema:                  Schema file, conforming to the JSON schema format, to validate upgraded
                                        config with.
        :param upgrade_merge_template:  If True then the template will be merged with the previous config at upgrade.
                                        If False then the template will only be used to initialise missing parameters.
                                        default=False.
        """

        # Check if this config is upgradable.
        upgradable, previous_version, previous_registration = self._check_upgradable(config)

        # If upgradable then we have a previous version of this config so can perform an upgrade.
        if upgradable:
            # Check whether config type has changed
            config_type_changed = config_type != previous_registration[CONST.cfg_type]

            (old_cfg,
             old_template,
             old_schema) = self._get_previous_config(previous_registration=previous_registration,
                                                     previous_version=previous_version)

            # Check if previous version has a template & if no template is specified for
            # this version then carry forward template from previous
            if (template is None
                    and old_template is not None
                    and not config_type_changed):
                template = old_template

            # Check if previous version has a schema & if no schema is specified for
            # this version then carry forward schema from previous
            if (schema is None
                    and old_schema is not None):
                # No, then carry forward schema from previous provided its valid
                schema = old_schema

            # Create the new registration
            self.__registered_cfg[config] = self._create_basic_registration(config,
                                                                            config_type)

            # Load new config type & validate
            cfg_type = self._load_and_validate_config_type(config_type)
            cfg_class = cfg_type.get(CFG_TYPE_CLASS)

            # Register new template
            if template is not None:
                self.__register_template(config,
                                         template,
                                         cfg_type.get(CFG_TYPE_EXT))

            # Register & load new schema
            schema_obj = None
            if schema is not None:
                self.__register_schema(config, schema)

                # Load the schema
                schema_obj = self.__get_schema_obj(schema)

            # Create new config
            cfg_obj = cfg_class(config_file=os.path.join(self.config_path,
                                                         self.__registered_cfg[config][CONST.cfg_fn]),
                                create=True)

            # Load template (Do not pass schema as we may need to use the default object for upgrade!)
            if upgrade_merge_template:
                # We are merging so load the template and initialise the cfg object
                cfg_template_obj = self.__init_from_template(cfg_obj=cfg_obj,
                                                             config_type=config_type,
                                                             template=template)

            else:
                # We are not merging so only load the template, do not initialise the cfg with template data
                cfg_template_obj = self._load_template(config_type=config_type,
                                                       template=template)

            if old_cfg is not None:
                self._validate_and_upgrade(old_cfg_obj=old_cfg,
                                           cfg_obj=cfg_obj,
                                           schema_obj=schema_obj,
                                           template_obj=cfg_template_obj)

            # Validate & Save config
            try:
                if schema is not None:
                    # Validate config against the schema
                    self.__validate_config(schema, cfg_obj)

            except ValidationError as err:
                logging.warning(u'Upgrade Failed, Configuration is invalid: {err}'.format(err=err))
                self.unregister(config)

            else:
                # Save the configuration
                cfg_obj.save()

                # Validate & save master config
                self.__validate_master_config()  # If invalid this raises either SchemaError or ValidationError.
                self.__master_cfg.save()

                logging.info(u'Configuration Upgraded: {cfg}'.format(cfg=config))

    @staticmethod
    def _validate_and_upgrade(old_cfg_obj,
                              cfg_obj,
                              schema_obj,
                              template_obj):

        # Upgrade the config
        for cfg_key, cfg_item in iter(old_cfg_obj.cfg.items()):
            cfg_obj.cfg[cfg_key] = cfg_item

        # Validate if required
        try:
            if schema_obj is not None:

                # Validate old config against the new schema
                v = Draft4Validator(schema_obj.cfg)

                # Attempt to handle basic validation errors
                for error in v.iter_errors(old_cfg_obj.cfg):
                    logging.debug(error.message)

                    item_key = u'.'.join(error.absolute_path) if error.absolute_path else None

                    matching_old_cfg_item = deepcopy(old_cfg_obj[item_key]
                                                     if item_key is not None
                                                     else old_cfg_obj.cfg)

                    # Attempt to handle required parameters (best effort to ensure required params get initialised)
                    if error.validator == u'required':
                        for prop in error.validator_value:
                            if prop not in matching_old_cfg_item:
                                logging.info(u'Adding missing required property ({p}) '
                                             u'for item ({i}).'.format(i=item_key,
                                                                       p=prop))

                                key = u'{k}.{p}'.format(k=item_key,
                                                        p=prop) if item_key is not None else prop

                                template_item_key = u'.'.join([TEMPLATE_DEFAULTS_ITEM]
                                                              + (list(error.absolute_path)[1:]
                                                                 if error.absolute_path else []))

                                template_key = u'{k}.{p}'.format(k=template_item_key,
                                                                 p=prop) if item_key is not None else template_item_key

                                try:
                                    # Attempt to get explicit template item
                                    # If template_obj is None: TypeError gets raised
                                    # If the property (value) is not in the template: KeyError gets raised
                                    cfg_obj[key] = template_obj[key]

                                except (TypeError, KeyError):

                                    try:
                                        # Attempt to get deafult item
                                        # If template_obj is None: TypeError gets raised
                                        # If the property (value) is not in the template: KeyError gets raised
                                        cfg_obj[key] = template_obj[template_key]

                                    except (TypeError, KeyError):
                                        properties = error.schema.get(u'properties')

                                        try:
                                            # If properties is None: TypeError gets raised
                                            # If the property (value) is not in the template: KeyError gets raised
                                            prop_type = properties[prop][u'type']

                                        except (TypeError, KeyError):
                                            raise error

                                        else:
                                            cfg_obj[key] = SCHEMA_TYPES[prop_type]()

                    # Attempt to handle additional properties (should be properties removed since last version)
                    elif error.validator == u'additionalProperties' and not error.validator_value:
                        logging.warning(u'Found Additional properties that are not allowed for item ({i}), '
                                        u'attempting to exclude individual properties.'.format(i=item_key))

                        allowed_properties = error.schema.get(u'properties')

                        if allowed_properties is not None:
                            # Use matching_old_cfg_item so we can do del on cfg_obj during iteration!
                            for prop in matching_old_cfg_item:
                                if prop not in allowed_properties:
                                    key = u'{k}.{p}'.format(k=item_key,
                                                            p=prop) if item_key is not None else prop

                                    logging.warning(u'Excluding: {k}.{p}'.format(k=item_key,
                                                                                 p=prop))

                                    del cfg_obj[key]

                    else:
                        logging.error(u'Unhandled schema validation error')
                        raise error

        except ValidationError as err:
            logging.warning(u'Old configuration is invalid with new schema, not upgrading: {err}'.format(err=err))

    def __check_loaded(self, config):

        """ Check whether config is already loaded.

        :param config:  The name of the config item being checked.
        :return: boolean.  True if already loaded.
        """

        if config not in self.__registered_cfg.keys():
            return False

        return True if config in self.__registered_cfg_objs.keys() else False

    def __register_template(self,
                            config,
                            template,
                            ext):

        """ Register a template to a config

        NOTE: This does not save the master config!

        :param config:      The config object to register the template to.
        :param template:    The path to the template being registered.
        :param ext:         The Template file extension.
        """

        if not os.path.exists(template):
            raise IOError(u'Template does not exists: {t}'.format(t=template))

        # Place a copy of the template in self.template_path
        ensure_path_exists(self.template_path)
        template_copy_fn = u'{cfg}.template.{ext}'.format(cfg=config,
                                                          ext=ext)
        template_copy = os.path.join(self.template_path, template_copy_fn)
        shutil.copyfile(template, template_copy)

        # Register the template
        self.__registered_cfg[config][CONST.cfg_template] = template_copy_fn

    def __register_schema(self,
                          config,
                          schema):

        """ Register a schema to a config

        NOTE: This does not save the master config!

        :param config:      The config object to register the template to.
        :param schema:      The path to the schema being registered.
        """

        if not os.path.exists(schema):
            raise IOError(u'Schema does not exists: {s}'.format(s=schema))

        # Place a copy of the schema in self.schema_path
        ensure_path_exists(self.schema_path)
        schema_copy_fn = u'{cfg}.schema.{ext}'.format(cfg=config,
                                                      ext=CONST.json)
        schema_copy = os.path.join(self.schema_path, schema_copy_fn)
        shutil.copyfile(schema, schema_copy)

        # Register the schema
        self.__registered_cfg[config][CONST.cfg_schema] = schema_copy_fn

    def __get_config_obj(self,
                         config):

        """ Get and return config object (loading it where necessary)

        :param config:  The config object requested
        :return:        An object exporting pre-defined config obj methods with the specified config loaded
        """

        if not self.__check_loaded(config):
            self.__load_cfg(config)

        return self.__registered_cfg_objs.get(config)

    @staticmethod
    def __get_schema_obj(schema_path):

        """ Loads and returns the schema object from the provided path.

        :param schema_path: Full path to schema file
        :return: Json schema object
        """

        # Load schema
        schema_type = CFG_TYPES.get(CONST.json)
        schema_class = schema_type.get(CFG_TYPE_CLASS)
        schema_obj = schema_class(config_file=schema_path)

        # Validate schema.  If invalid this will raise SchemaError
        Draft4Validator.check_schema(schema_obj.cfg)

        return schema_obj

    def _get_previous_config(self,
                             previous_registration,
                             previous_version):

        previous_config_path = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                            previous_version,
                                            CONST.cfg_dir)

        # Load previous config type & validate
        previous_cfg_type = self._load_and_validate_config_type(previous_registration[CONST.cfg_type])
        previous_cfg_class = previous_cfg_type.get(CFG_TYPE_CLASS)

        # Load the previous config
        old_cfg = previous_cfg_class(config_file=os.path.join(previous_config_path,
                                                              previous_registration[CONST.cfg_fn]))

        # Check if previous version has a template
        previous_template_fn = previous_registration.get(CONST.cfg_template)
        previous_template = None

        if previous_template_fn:
            previous_template = os.path.join(previous_config_path,
                                             previous_template_fn)

        # Check if previous version has a schema
        old_config_invalid = False
        old_schema_invalid = False

        previous_schema_fn = previous_registration.get(CONST.cfg_schema)
        previous_schema = None

        if previous_schema_fn is not None:
            previous_schema = os.path.join(previous_config_path,
                                           previous_schema_fn)

            if os.path.exists(previous_schema):
                # Validate the previous config against its own schema
                try:
                    self.__validate_config(previous_schema, old_cfg)

                except SchemaError as err:
                    logging.error(u'Invalid schema for old config: {err}'.format(err=err))
                    old_schema_invalid = True

                except ValidationError as err:
                    logging.error(u'Old configuration is invalid: {err}'.format(err=err))
                    old_config_invalid = True

        return (None if old_config_invalid else old_cfg,
                previous_template,
                None if old_schema_invalid else previous_schema)

    def __validate_config(self,
                          schema_path,
                          obj):

        """ Validate the provided config object against its schema if a schema is available.

        :param schema_path:  The path to the schema file to be used for validation
        :param obj:          The Config object to be validated
        """

        # Load schema
        schema_obj = self.__get_schema_obj(schema_path)

        if u'properties' in schema_obj:
            # Make sure schema has reference to TEMPLATE_DEFAULTS_ITEM!
            if TEMPLATE_DEFAULTS_ITEM not in schema_obj[u'properties']:
                schema_obj[u'properties'][TEMPLATE_DEFAULTS_ITEM] = {u'type': u'object'}

        # Ensure loaded config is still valid (i.e any external modification hasn't corrupted it)
        validator = Draft4Validator(schema_obj.cfg)
        validator.validate(obj.cfg)

    def __validate_master_config(self):

        """ Validate the master config object against its schema.

        """

        # Ensure master config is still valid (i.e any modification hasn't corrupted it)
        validator = Draft4Validator(self.__master_cfg_schema_obj.cfg)
        validator.validate(self.__master_cfg.cfg)

    def __validate_registered_config(self,
                                     config,
                                     obj):

        """ Validate the provided config object against its schema if a schema is available.

        :param config: The config that the config object relates to (so we can retrieve the schema
        :param obj:    The Config object to be validated
        """

        cfg = self.__registered_cfg.get(config)
        schema = cfg.get(CONST.cfg_schema)

        if schema is not None:
            # Load schema
            schema_path = os.path.join(self.schema_path, schema)
            self.__validate_config(schema_path, obj)

    def __validate_and_save_registered_config(self,
                                              config,
                                              obj):

        """ Validate the provided config object against its schema if a schema is available
            saving the config on successful validation.

        :param config: The config that the config object relates to (so we can retrieve the schema
        :param obj:    The Config object to be validated
        """

        # Validate the config
        try:
            self.__validate_registered_config(config, obj)

        except ValidationError:
            # Reload the config to keep the config valid
            self.__reload_cfg(config)

            # pass the exception on
            raise

        else:
            # If all is well we can save the object
            obj.save()

    def __validate_config_key(self, key):

        """ Get and return config item

        :param key: The config key to be validated
        :return:    obj - The config object for the validated config key,
                    config - The entry from the registered config dict,
                    items - List of items to traverse for the requested config value.
        """

        keys = key.split(u'.')

        if len(keys) > 1:

            config = keys[0]
            items = u'.'.join(keys[1:])

        else:
            # We requested the entire config file?!
            config = key
            items = None

        obj = self.__get_config_obj(config)  # This will raise a KeyError if the config is not registered.

        return obj, config, items

    def __getitem__(self, key):

        """ Get and return config item

        :param key: The config key used to retrieve the config item
        :return:    The requested config item
        """

        obj, config, items = self.__validate_config_key(key)

        if items is None:
            # Entire config was requested!
            return obj.cfg

        else:
            try:
                return obj[items]

            except KeyError:
                raise KeyError(u'Item key ({i}) not found'.format(i=key))

    def __setitem__(self, key, value):

        """ Set and return config item

        :param key:     The config key used to retrieve the config item
        :param value:   The new value for the config item
        """

        obj, config, items = self.__validate_config_key(key)

        # Update the config
        if items is None:
            # Entire config overwrite was requested!
            obj.cfg = value

        else:
            # Update & validate the item (where schema is present)
            # This includes adding any nodes that don't already exist
            obj[items] = value

        # Validate & save the config
        self.__validate_and_save_registered_config(config, obj)

    def __delitem__(self, key):

        """ Delete the specified config item

        :param key: The config key used to retrieve the config item being deleted
        """

        obj, config, items = self.__validate_config_key(key)

        if items is None:
            # Delete entire config?!  This is what the unregister function is for!
            # We raise an error rather than call unregister for the user to avoid accidental config removal!
            raise ValueError(u'Removal of the entire config via the del method is not supported; '
                             u'Please use the Configuration.unregister method instead!')

        else:
            # Delete & validate the item (where schema is present)
            del obj[items]

            # Validate & save the config
            self.__validate_and_save_registered_config(config, obj)

    def find(self,
             key,
             filters=None):

        """ Get a filtered list of config items

        NOTE: Find is not recursive and will only search the first level of the key provided.

        :param key:     The config item to run the search on.
        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
                        NOTE: if filters is None the entire key value will be returned.
        :return: dict containing the subset of matching items
        """

        # This will raise a KeyError if the config is not registered.
        obj, _, items = self.__validate_config_key(key)

        return obj.find(items, filters)

    def get_temp_path(self,
                      folder=None):

        folder_path = self.temp_path

        if folder:
            folder_path = os.sep.join((folder_path, folder))

        ensure_path_exists(folder_path)

        return folder_path

    @staticmethod
    def validate_version(version):
        return bool(re.match(r'^(\d+\.)?(\d+\.)?(\d+)$', version))

    def normalise_version(self,
                          version):
        """ Drops trailing zeros from version number. """
        normalised = self.split_version(version)

        while normalised[-1] == 0:
            normalised.pop()

        return self.join_version(normalised)

    @staticmethod
    def split_version(version):
        return lmap(int, version.split(u'.'))

    def split_versions(self,
                       versions):
        return [self.split_version(version) for version in versions]

    @staticmethod
    def join_version(version):
        return u'.'.join(lmap(newstr, version))

    def join_versions(self,
                      versions):
        return [self.join_version(version) for version in versions]

    def _validate_current_version(self,
                                  version):

        """ Validate current version is the latest version.

        :param version  The version to compare with the current version.

        :return         True when current is latest or versions equal.
                        False when current not latest.

        """

        if version is None:
            return True

        curr = self.split_version(self.normalise_version(self.app_version))
        old = self.split_version(self.normalise_version(version))

        return True if cmp(curr, old) >= 0 else False

    def __get_previous_versions(self,
                                path):

        """ Check for and return the previous versions available

        :param path: The path in which to check for previous versions.

        :return:     List of version numbers (strings).
        """

        valid_previous_versions = []

        for item in os.listdir(path):
            if self.validate_version(item):
                valid_previous_versions.append(self.normalise_version(item))

        previous_versions = self.join_versions(sorted(self.split_versions(valid_previous_versions)))

        return previous_versions

    def __get_last_version(self):

        """ Work out the latest version of the app installed (not including the loaded version)

        Note: logs a warning if current version is older than the latest available

        :return: version number (string)
        """

        # Get the previous versions
        previous_versions = self.previous_versions

        #  filter out the current version
        if self.app_version in previous_versions:
            del previous_versions[previous_versions.index(self.app_version)]

        last_version = previous_versions.pop() if len(previous_versions) > 0 else None

        if not self._validate_current_version(last_version):
            logging.warning(u'You are running a version of config ({ver}) '
                            u'older than has been previously installed ({old_ver})!'.format(ver=self.app_version,
                                                                                            old_ver=last_version))

        return last_version

    # Properties
    @property
    def config_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_dir)

    @property
    def schema_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_schema)

    @property
    def template_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_template)

    @property
    def data_path(self):
        return self.__app_dirs.user_data_dir

    @property
    def data_path_unversioned(self):
        return self.__basic_app_dirs.user_data_dir

    @property
    def cache_path(self):
        return self.__basic_app_dirs.user_cache_dir

    @property
    def log_path(self):
        return self.__basic_app_dirs.user_log_dir

    @property
    def temp_path(self):
        return self.__temp_path

    @property
    def plugin_path(self):
        return os.path.join(self.data_path_unversioned, u'plugins')

    @property
    def app_name(self):
        return self.__app_kwargs.get(u'appname')

    @property
    def app_version(self):
        return self.__app_kwargs.get(u'version')

    @property
    def app_author(self):
        return self.__app_kwargs.get(u'appauthor')

    @property
    def previous_versions(self):
        return self.__get_previous_versions(self.__app_dirs_all_versions.user_config_dir)

    @property
    def last_version(self):
        return self.__get_last_version()
