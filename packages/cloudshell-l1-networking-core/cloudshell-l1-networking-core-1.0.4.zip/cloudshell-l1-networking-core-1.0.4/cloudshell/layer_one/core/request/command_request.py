#!/usr/bin/python
# -*- coding: utf-8 -*-


class CommandRequest(object):
    def __init__(self, command_name, command_id, command_params):
        """
        Command request entity
        :param command_name: 
        :param command_id: 
        :param command_params:
        :type command_params: dict
        """
        self.command_name = command_name
        self.command_id = command_id
        self.command_params = command_params

    def __str__(self):
        return 'Command: {0}, {1}, {2}'.format(self.command_name, self.command_id, self.command_params)

    def __repr__(self):
        return self.__str__()
