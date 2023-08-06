# -*- coding: utf-8 -*-

from ct_manager.enums import MiscSetting


class SettingsFactory(object):
    def __init__(self, config='config.yaml'):
        self._misc_setting = MiscSetting.EmailSetting
        self._config = config
        self._pg_user = 'postgres'
        self._xrisk_user = ''
        self._xrisk_password = ''
        self._remote_user = ''
        self._remote_password = ''

    @property
    def postgres_user(self):
        return self._pg_user

    @postgres_user.setter
    def postgres_user(self, user):
        self._pg_user = user

    @property
    def xrisk_user(self):
        return self._xrisk_user

    @xrisk_user.setter
    def xrisk_user(self, user):
        self._xrisk_user = user

    @property
    def xrisk_password(self):
        return self._xrisk_password

    @xrisk_password.setter
    def xrisk_password(self, password):
        self._xrisk_password = password

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    @property
    def misc_setting(self):
        return self._misc_setting

    @misc_setting.setter
    def misc_setting(self, setting):
        self._misc_setting = setting

    @property
    def remote_server_user(self):
        return self._remote_user

    @remote_server_user.setter
    def remote_server_user(self, user):
        self._remote_user = user

    @property
    def remote_server_password(self):
        return self._remote_user

    @remote_server_password.setter
    def remote_server_password(self, password):
        self._remote_password = password


Settings = SettingsFactory()
