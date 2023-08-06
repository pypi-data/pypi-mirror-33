# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 23, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals
from voluptuous import message, Invalid, All, Length, Url, Schema
import os
import re
from configobj import ConfigObj

from darkskysync.Exceptions import ConfigurationError
from darkskysync.DataSource import DataSource
from darkskysync.LocalFileSystem import LocalFileSystem
from darkskysync.RemoteFactory import SSHRemoteLocationFactory

class DataSourceFactory(object):
    '''
    A factory creating DataSource configurations
    '''

    DEFAULT_CONFIGURATION_FILE = os.path.expanduser(
    "~/.darkskysync/config")

    REMOTE_FACTORY_TYPE_MAP = {"rsync": SSHRemoteLocationFactory,
                               "ssh": SSHRemoteLocationFactory,
                               "local": SSHRemoteLocationFactory}

    def __init__(self, config):
        '''
        Constructor
        '''
        self.config = config
        validator = ConfigValidator(self.config)
        validator.validate()


    @classmethod
    def fromConfig(cls, configfile):
        """
        Helper method to initialize DataSourceFactory from an ini file.
        :param configfile: path to the ini file
        :return: configurator object
        """
        config_reader = ConfigReader(configfile)
        conf = config_reader.read_config()
        return DataSourceFactory(conf)

    def createDataSource(self, template, name=None):
        """
        Creates a data source by inspecting the configuration properties of the
            given data source template.
        :param template: name of the data source template

        :param name: name of the data source. If not defined, the data source
        will be named after the template.

        :return: :py:class:`DataSource` instance

        :raises ConfigurationError: data source template not found in config
        """
        if not name:
            name = template

        if template not in self.config:
            raise ConfigurationError(
                "Invalid configuration for data source `%s`: %s"
                "" % (template, name))

        conf = self.config[template]

        extra = conf['datasource'].copy()
        extra.pop('local')
        extra.pop('remote')

        return DataSource(template,
                          self.createLocal(template),
                          self.createRemote(template))

    def createLocal(self, template):
        conf = self.config[template]

        return LocalFileSystem(conf["datasource"]["local"], conf["local"]["path"])

    def createRemote(self, template):

        conf = self.config[template]
        remoteType = conf["remote"]["type"]

        RemoteFactory = DataSourceFactory.REMOTE_FACTORY_TYPE_MAP[remoteType]

        factory = RemoteFactory()

        return factory.create(conf["datasource"]["remote"], conf)

class ConfigValidator(object):

    def __init__(self, config):
        self.config = config


    def _pre_validate(self):
        """
        Handles all pre validation phase functionality, such as:
        - reading environment variables
        - interpolating configuraiton options
        """

    def _post_validate(self):
        """
        Handles all post validation phase functionality, such as:
        - expanding file paths
        """
        # expand all paths
        for dataSource, values in self.config.items():
            conf = self.config[dataSource]

            privkey = os.path.expanduser(values['login']['known_hosts'])
            conf['login']['known_hosts'] = privkey

            privkey = os.path.expanduser(values['login']['user_key_private'])
            conf['login']['user_key_private'] = privkey

            pubkey = os.path.expanduser(values['login']['user_key_public'])
            conf['login']['user_key_public'] = pubkey

            path =  os.path.expanduser(values['local']['path'])
            conf['local']['path'] = path

    def validate(self):
        """
        Validates the given configuration :py:attr:`self.config` to comply.
        As well all types are converted to the expected
        format if possible.
        """
        self._pre_validate()

        # custom validators
        @message("file could not be found")
        def check_file(v):
            f = os.path.expanduser(os.path.expanduser(v))
            if os.path.exists(f):
                return f
            else:
                raise Invalid("file could not be found `%s`" % v)

        # schema to validate all dataSource properties
        schema = {"datasource": {"local": All(str, Length(min=1)),
                              "remote": All(str, Length(min=1)),
                              },
                  "local": {"path": All(str, Length(min=1)), #check_file(),
                            },
                  "login": {"name": All(str, Length(min=1)),
                            "known_hosts": check_file(),
                            "user_key_private": check_file(),
                            "user_key_public": check_file(),
                            }
                  }

        remote_schema_ssh = {"type": 'ssh',
                            "host": Url(str),
                            "port": All(str, Length(min=1)),
                            "path": All(str, Length(min=0)),
                            "login": All(str, Length(min=1))}

        # validation
        validator = Schema(schema, required=True, extra=True)
        ssh_validator = Schema(remote_schema_ssh, required=True, extra=False)

        if not self.config:
            raise Invalid("No data sources found in configuration.")

        for dataSource, properties in self.config.items():
            validator(properties)

            if properties['remote']['type'] == "ssh":
                ssh_validator(properties['remote'])

        self._post_validate()


class ConfigReader(object):
    """
    Reads the configuration properties from a ini file.
    """
    local_section = "local"
    remote_section = "remote"
    login_section = "login"
    datasource_section = "datasource"

    def __init__(self, configfile):
        """
        :param configfile: path to configfile
        """
        self.configfile = configfile
        self.conf = ConfigObj(self.configfile, interpolation=False)

    def read_config(self):
        """
        Reads the configuration properties from the ini file and links the
        section to comply with the datasource config dictionary format.
        :return: dictionary containing all configuration properties from the
         ini file in compliance to the datasource config format
        :raises MultipleInvalid: not all sections present or broken links
            between secitons
        """
        datasources = dict((key, value) for key, value in self.conf.items() if
                        re.search(ConfigReader.datasource_section + "/(.*)", key)
                        and key.count("/") == 1)

        conf_values = dict()

        for datasource in datasources:
            name = re.search(ConfigReader.datasource_section + "/(.*)",
                             datasource).groups()[0]
            try:
                datasource_conf = dict(self.conf[datasource])
                local_name = ConfigReader.local_section + "/" + datasource_conf[
                    "local"]
                remote_name = ConfigReader.remote_section + "/" + datasource_conf[
                    "remote"]

                values = dict()
                values['datasource'] = datasource_conf
                values['local'] = dict(self.conf[local_name])
                values['remote'] = remote_conf = dict(self.conf[remote_name])

                login_name = ConfigReader.login_section + "/" + remote_conf[
                    'login']

                values['login'] = dict(self.conf[login_name])

                conf_values[name] = values
            except KeyError:
                raise Exception(
                    "could not find all sections required `datasource`, "
                    "`setup`, \ `login`, `cloud` for datasource `%s`" % name)

        return conf_values
