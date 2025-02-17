# This script can be used for testing FTP upload/download performance
# It mimics behavior of JMeter FTP sampler
# Author: Marcin Kowalczyk (github.com/kowalpy)

import datetime
import ftplib
import os
import time

from locust import User


class FtpUser(User):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.client = FtpClient(environment=environment)


class FtpClient:
    def __init__(self, environment):
        self.environment = environment
        self.connection = None
        self.user = None
        self.host = None

    def connect(self, user="anonymous", password="anonymous@", port=21, timeout=5, tls=False, passive_mode=False):
        self.user = user
        if tls:
            self.connection = ftplib.FTP_TLS()
        else:
            self.connection = ftplib.FTP()
        self.connection.connect(self.environment.host, port, timeout)
        self.connection.login(user, password)
        self.connection.set_pasv(passive_mode)

    def change_working_dir(self, dir_name):
        self.connection.cwd(dir_name)

    def download_file(self, remote_file_name, local_dir_path):
        local_dir_path = os.path.normpath(local_dir_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        local_file_path = os.path.join(local_dir_path, timestamp)
        start_perf_counter = time.perf_counter()
        exception = None
        response = ""
        try:
            with open(local_file_path, "wb") as local_file:
                response = self.connection.retrbinary("RETR " + remote_file_name, local_file.write)
                response_time = (time.perf_counter() - start_perf_counter) * 1000
        except ftplib.all_errors as e:
            exception = e
            response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="get",
                name=remote_file_name,
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
        else:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="get",
                name=remote_file_name,
                response_time=response_time,
                response_length=len(response),
            )

        return local_file_path

    def upload_file(self, local_file_path):
        local_file_path = os.path.normpath(local_file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        remote_dir_file = timestamp
        start_perf_counter = time.perf_counter()
        exception = None
        response = ""
        try:
            response = self.connection.storbinary("STOR " + remote_dir_file, open(local_file_path, "rb"))
        except ftplib.all_errors as e:
            exception = e
        response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="send",
                name=local_file_path,
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
        else:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="send",
                name=local_file_path,
                response_time=response_time,
                response_length=len(response),
            )

        return remote_dir_file

    def delete_file(self, remote_file_name):
        start_perf_counter = time.perf_counter()
        exception = None
        response = ""
        try:
            response = self.connection.delete(remote_file_name)
            response_time = (time.perf_counter() - start_perf_counter) * 1000
        except ftplib.all_errors as e:
            exception = e
            response_time = (time.perf_counter() - start_perf_counter) * 1000

        if exception:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="delete",
                name=remote_file_name,
                exception=exception,
                response_time=response_time,
                response_length=len(str(exception)),
            )
        else:
            self.environment.events.request.fire(
                request_type="FTP",
                request_method="delete",
                name=remote_file_name,
                response_time=response_time,
                response_length=len(response),
            )

    def disconnect(self):
        self.connection.close()
