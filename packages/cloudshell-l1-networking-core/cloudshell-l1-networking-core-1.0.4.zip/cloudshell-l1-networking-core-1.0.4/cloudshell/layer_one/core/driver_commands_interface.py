#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class DriverCommandsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def login(self, address, username, password):
        """
        Login driver command, 
        :param address: 
        :param username: 
        :param password: 
        :return: 
        """
        pass

    @abstractmethod
    def get_resource_description(self, address):
        """
        GetResourceDescription driver command
        :param address: 
        :return: 
        """
        pass

    @abstractmethod
    def map_bidi(self, src_port, dst_port):
        """
        MapBidi driver command
        :param src_port: 
        :param dst_port: 
        :return: 
        """
        pass

    @abstractmethod
    def map_uni(self, src_port, dst_ports):
        """
        MapUni driver command
        :param src_port: 
        :param dst_ports:
        :return: 
        """
        pass

    @abstractmethod
    def map_clear_to(self, src_port, dst_ports):
        """
        MapClearTo driver command
        :param src_port: 
        :param dst_ports:
        :return: 
        """
        pass

    @abstractmethod
    def map_clear(self, ports):
        """
        MapClear driver command
        :param ports: 
        :return: 
        """
        pass

    @abstractmethod
    def get_attribute_value(self, address, attribute_name):
        """
        GetAttributeValue driver command
        :param address: 
        :param attribute_name: 
        :return: 
        """
        pass

    @abstractmethod
    def set_attribute_value(self, address, attribute_name, attribute_value):
        """
        SetAttributeValue driver command
        :param address: 
        :param attribute_name: 
        :param attribute_value: 
        :return: 
        """
        pass

    @abstractmethod
    def get_state_id(self):
        """
        GetStateId driver command
        :return: 
        """
        pass

    @abstractmethod
    def set_state_id(self, state_id):
        """
        SetStateId driver command
        :param state_id: 
        :return: 
        """
        pass

    @abstractmethod
    def map_tap(self, src_port, dst_ports):
        """
        MapTap driver command
        :param src_port: 
        :param dst_ports:
        :return: 
        """
        pass

    @abstractmethod
    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        Set connection speed
        Is not used for the new standard
        :param src_port:
        :param dst_port:
        :param speed:
        :param duplex:
        :return:
        """
        pass
