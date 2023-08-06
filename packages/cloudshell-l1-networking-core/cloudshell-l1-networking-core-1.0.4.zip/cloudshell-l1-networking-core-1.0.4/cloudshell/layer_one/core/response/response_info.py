#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from xml.etree.ElementTree import Element

from cloudshell.layer_one.core.response.resource_info.resource_info_builder import ResourceInfoBuilder


class ResponseInfo(object):
    """
    Basic response builder
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_xml_node(self):
        """Build xml node"""
        pass

    @staticmethod
    def _build_response_info_node():
        return Element('ResponseInfo')


class ResourceDescriptionResponseInfo(ResponseInfo):
    """Resource description builder"""

    def __init__(self, resource_info):
        if isinstance(resource_info, list):
            self.resource_info_list = resource_info
        else:
            self.resource_info_list = [resource_info]

    def build_xml_node(self):
        """Build xml node for resource description"""
        response_info_node = self._build_response_info_node()
        response_info_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        response_info_node.attrib['xsi:type'] = "ResourceInfoResponse"
        for resource_info in self.resource_info_list:
            response_info_node.append(ResourceInfoBuilder.build_resource_info_nodes(resource_info))
        return response_info_node


class KeyValueResponseInfo(ResponseInfo):
    """Simple key value builde, used for Get/Set attribute"""

    def __init__(self, attributes_dict):
        """
        :param attributes_dict:
        :type attributes_dict: dict
        """
        self.attributes_dict = attributes_dict

    def build_xml_node(self):
        response_info_node = self._build_response_info_node()
        for name, value in self.attributes_dict.iteritems():
            attribute_node = Element(name)
            attribute_node.text = value
            response_info_node.append(attribute_node)
        return response_info_node


class GetStateIdResponseInfo(ResponseInfo):
    ATTRIBUTE_NAME = 'StateId'

    def __init__(self, state_id):
        self._state_id = str(state_id)

    def build_xml_node(self):
        response_info_node = self._build_response_info_node()
        response_info_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        response_info_node.attrib['xsi:type'] = "StateInfo"
        attribute_node = Element(self.ATTRIBUTE_NAME)
        attribute_node.text = self._state_id
        response_info_node.append(attribute_node)
        return response_info_node


class AttributeValueResponseInfo(ResponseInfo):
    ATTRIBUTE_NAME = 'Value'

    def __init__(self, value):
        self._value = value if value else 'NA'

    def build_xml_node(self):
        response_info_node = self._build_response_info_node()
        response_info_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        response_info_node.attrib['xsi:type'] = "AttributeInfoResponse"
        attribute_node = Element(self.ATTRIBUTE_NAME)
        attribute_node.text = self._value
        response_info_node.append(attribute_node)
        return response_info_node
