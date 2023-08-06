#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime


class CommandResponse(object):
    def __init__(self, command_request):
        """
        Command response
        :param command_request:
        :type command_request: cloudshell.layer_one.core.request.command_request.CommandRequest
        """
        self.command_request = command_request

        # Response attributes
        self.success = False
        self.error = None
        self.log = None
        self.timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.response_info = None

    def __str__(self):
        return 'Command: {0}, {1}, {2}'.format(self.command_request.command_name, self.command_request.command_id,
                                               self.command_request.command_params)

    def __repr__(self):
        return self.__str__()
