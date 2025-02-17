# This script is an example of testing FTP download performance
# It mimics behavior of JMeter FTP sampler
# Author: Marcin Kowalczyk (github.com/kowalpy)

import os
from time import sleep

from locust import task, between
from locust_plugins.users.ftp import FtpUser

local_dir = "<local_dir_containing_files_for_upload_at_your_pc>"
remote_dir = "<subdir_at_ftp_server_where_files_should_be_uploaded>"


class FtpTestUpload(FtpUser):
    wait_time = between(5, 10)

    def on_start(self):
        # on start, you must connect to ftp server
        self.client.connect(user="admin", password="admin")
        # optionally, you may want to change your working dir at ftp server
        self.client.change_working_dir(remote_dir)

    @task
    def upload_file_1(self):
        # testing ftp file download
        self.client.upload_file(os.path.join(local_dir, "example_file.txt"))

    @task
    def upload_file_2(self):
        # testing ftp file download, wait 1 second and delete it
        uploaded_file = self.client.upload_file(os.path.join(local_dir, "example_file_2.txt"))
        sleep(1)
        self.client.delete_file(uploaded_file)


    @task
    def upload_file_incorrect(self):
        # testing ftp file download - failure expected
        self.client.upload_file(os.path.join(local_dir, "example_not_existing.txt"))

    def on_stop(self):
        # it is a good practice to close connection once tests are completed
        self.client.disconnect()
