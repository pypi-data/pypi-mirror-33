# -*- coding: utf-8 -*-

try:
    import paramiko
except ImportError:
    pass

from ct_manager.base_handler import SimpleDataHanlder
from ct_manager.enums import DataSource
from ct_manager.settings import Settings


class RemoteHandler(SimpleDataHanlder):
    def __init__(self, **kwargs):
        super(RemoteHandler, self).__init__(data_source=DataSource.REMOTE_FOLDER, **kwargs)
        self.user = Settings.remote_server_user
        self.password = Settings.remote_server_password
        self.host = self.connector_params['host']
        self.port = self.connector_params['port']
        self.transport, self.sftp_client = self.init_connect()

    def init_connect(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.user, password=self.password)  # 登录远程服务器
        return transport, paramiko.SFTPClient.from_transport(transport)

    def close(self):
        if self.sftp_client is not None:
            self.sftp_client.close()

    def download(self, remote_path, local_path):
        self.sftp_client.get(remote_path, local_path)






