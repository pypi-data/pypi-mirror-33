import re
import socket
import traceback
from threading import Thread

from cloudshell.layer_one.core.request.requests_parser import RequestsParser
from cloudshell.layer_one.core.response.command_responses_builder import CommandResponsesBuilder


class ConnectionClosedException(Exception):
    pass


class ConnectionHandler(Thread):
    """
    Handle connections
    """
    REQUEST_END = r'</Commands>'
    END_COMMAND = '\r\n'
    READ_TIMEOUT = 30

    def __init__(self, connection_socket, command_executor, xml_logger, logger, buffer_size=2048):
        """
        :param connection_socket:
        :type connection_socket: socket.socket
        :param command_executor:
        :type command_executor: cloudshell.layer_one.core.command_executor.CommandExecutor
        :param xml_logger: 
        :param logger: 
        :param buffer_size: 
        """
        super(ConnectionHandler, self).__init__()
        self._connection_socket = connection_socket
        self._xml_logger = xml_logger
        self._logger = logger
        self._command_executor = command_executor
        self._buffer_size = buffer_size

    def run(self):
        """Start handling new connection"""
        while True:
            try:
                command_requests = self._read_request_commands()
                responses = self._command_executor.execute_commands(command_requests)
                self._send_response(
                    CommandResponsesBuilder.to_string(CommandResponsesBuilder.build_xml_result(responses)))
            except ConnectionClosedException:
                self._connection_socket.close()
                self._logger.debug('Connection closed by remote host')
                break
            except socket.timeout:
                self._connection_socket.close()
                self._logger.debug('Connection closed by timeout')
                break
            except Exception as ex:
                self._send_response(
                    CommandResponsesBuilder.to_string(CommandResponsesBuilder.build_xml_error(0, ex.message)))
                tb = traceback.format_exc()
                self._logger.critical(tb)
                self._connection_socket.close()
                break

    def _read_socket(self):
        """
        Read data from socket
        :return: 
        """
        self._connection_socket.settimeout(self.READ_TIMEOUT)
        data = ''
        while True:
            input_buffer = self._connection_socket.recv(self._buffer_size)
            if not input_buffer:
                raise ConnectionClosedException()
            else:
                data += input_buffer.strip()
                if re.search(self.REQUEST_END, data):
                    break

        return data

    def _read_request_commands(self):
        """Read data and create requests"""
        request_string = self._read_socket()
        self._xml_logger.info(request_string.replace('\r', '') + "\n\n")
        requests = RequestsParser.parse_request_commands(request_string)
        self._logger.debug(requests)
        return requests

    def _send_response(self, response_string):
        """
        Send response
        :param response_string: 
        :return: 
        """
        self._connection_socket.send(response_string + self.END_COMMAND + self.END_COMMAND)
        self._xml_logger.info(response_string)
