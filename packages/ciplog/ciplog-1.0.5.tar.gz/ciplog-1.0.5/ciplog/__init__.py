from datetime import datetime
import glob
import os
import logging
import logging.handlers
import logging.config
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from .json_log_formatter import JSONFormatter

SERVICE_NAME = "cip_log"
LOG_PATH = "{}/log/".format(os.getcwd())

HTTP_STATUS = [
    100, 101, 102, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 301, 302, 303, 304, 305, 306,
    307, 308, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417,
    422, 423, 424, 426, 428, 429, 431, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511
    ]


ERROR = {
    'code': "HS001",
    'message': 'valor do status HTTP é inválido'
}


class CipLog(object):

    def __init__(self, service_name=SERVICE_NAME, log_path=LOG_PATH, scope_name=__name__):

        self._max_file_size = 500000
        self._log_folder = log_path
        self.service_name = service_name

        self.create_folder()

        file_name = datetime.now().strftime('%d-%m-%Y.log')
        file_path = "{0}{1}".format(self._log_folder, file_name)
        formatter = JSONFormatter()

        file_handler = RotatingFileHandler(file_path, maxBytes=self._max_file_size, backupCount=20)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)

        self._logger = logging.getLogger(scope_name)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(stream_handler)
        self._logger.setLevel(logging.DEBUG)

    def create_folder(self):
        if not os.path.exists(self._log_folder):
            os.makedirs(self._log_folder)

    def path(self):
        """Return the path of the logs folder.
        For default, path is your folder.
        """
        return self._log_folder

    def service_name_log(self):
        """service name that used in info, warning and error."""
        return self.service_name

    @staticmethod
    def validate_status_http(status_code):
        """validate status http, if invaluable call the function warning"""
        if status_code in HTTP_STATUS:
            return True
        return False

    def count_log_files(self):
        """Return number of log files."""
        return len(glob.glob("{0}/*.log*".format(self._log_folder)))

    def get_log_files(self):
        """Return all logs files."""
        return glob.glob("{0}/*.log*".format(self._log_folder))

    def delete_log_files(self):
        for file in glob.glob("{0}/*.log*".format(self._log_folder)):
            try:
                os.remove(file)
            except IOError as io:
                self.error("erro ao excluir")

    def debug(self, message):
        self._logger.debug(message)

    def info(self, status, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - status (int): Is a HTTP response status code.
            - service_name (str): Service name the of application.
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        if CipLog.validate_status_http(status):
            self._logger.info(message, extra={'level': 'INFO', 'status_code': status, 'service_name': service_name})
        else:
            self.warning(code=ERROR['code'], service_name=None, message=ERROR['message'])

    def warning(self, code, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - code (str): One value that define the message log.
            - service_name (str): Service name the of aplication.
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        self._logger.warning(message, extra={'level': 'WARNING', 'code': code, 'service_name': service_name})

    def error(self, code, status, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - code (str): One value that define the message log.
            - status (int): Is a HTTP reponse status code.
            - service_name (str): Service name the of aplication.
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        if self.validate_status_http(status):
            self._logger.error(message,
                               extra={'level': 'ERROR', 'code': code, 'status_code': status, 'service_name': service_name},
                               exc_info=True)
        else:
            self.warning(code='HS001', service_name=service_name, message='valor do status http e invalido.')
