# This script is an example of testing FTP download performance
# It mimics behavior of JMeter FTP sampler
# Author: Marcin Kowalczyk (github.com/kowalpy)

from locust import task, between
from locust_plugins.users.ftp import FtpUser

local_dir = "<local_dir_to_save_downloaded_files_at_your_pc>"
remote_dir = "<subdir_at_ftp_server_where_files_to_download_are>"


class FtpTestDownload(FtpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # on start, you must connect to ftp server
        self.client.connect(user="admin", password="admin")
        # optionally, you may want to change your working dir at ftp server
        self.client.change_working_dir(remote_dir)

    @task
    def get_file_1(self):
        # testing ftp file download
        self.client.download_file("example_file.txt", local_dir)

    @task
    def get_file_2(self):
        # testing ftp file download
        self.client.download_file("example_file_2.txt", local_dir)

    @task
    def get_file_incorrect(self):
        # testing ftp file download - failure expected
        self.client.download_file("example_not_existing.txt", local_dir)

    def on_stop(self):
        # it is a good practice to close connection once tests are completed
        self.client.disconnect()
