#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cloudshell.layer_one.core.helper.xml_helper import XMLHelper


def full_path(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


class ResourceInfoBuilder(object):
    """
    Build resource info node
    """
    RESOURCE_TEMPLATE = XMLHelper.read_template(full_path('templates/resource_template.xml'))
    ATTRIBUTE_TEMPLATE = XMLHelper.read_template(full_path('templates/resource_attribute_template.xml'))
    MAPPING_TEMPLATE = XMLHelper.read_template(full_path('templates/resource_incoming_map_template.xml'))

    @staticmethod
    def _build_resource_node(resource_info):
        """
        Build resource xml node
        :param resource_info:
        :type resource_info: cloudshell.layer_one.core.response.entities.base.ResourceInfo
        :return: Resource node
        :rtype: xml.etree.ElementTree.Element
        """
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.RESOURCE_TEMPLATE)
        node.set("Name", resource_info.name)
        node.set("ResourceFamilyName", resource_info.family_name)
        node.set("ResourceModelName", resource_info.model_name)
        node.set("SerialNumber", resource_info.serial_number)
        node.set("Address", resource_info.address)
        attributes_node = node.find("ResourceAttributes")
        for attribute in resource_info.attributes:
            attribute_node = ResourceInfoBuilder._build_attribute_node(attribute)
            attributes_node.append(attribute_node)
        if resource_info.mapping:
            node.append(ResourceInfoBuilder._build_mapping_node(resource_info.mapping))
        return node

    @staticmethod
    def _build_attribute_node(attribute):
        """
        Build attribute node
        :param attribute: 
        :type attribute: cloudshell.layer_one.core.response.entities.base.Attribute
        :return: Attribute node
        :rtype: xml.etree.ElementTree.Element
        """
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.ATTRIBUTE_TEMPLATE)
        node.set("Name", attribute.name)
        node.set("Type", attribute.type)
        node.set("Value", attribute.value)
        return node

    @staticmethod
    def _build_mapping_node(mapping_node):
        """
        Build mapping node
        :param mapping_node: 
        :type mapping_node: cloudshell.layer_one.core.response.entities.base.ResourceInfo
        :return: Mapping node
        :rtype: xml.etree.ElementTree.Element
        """
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.MAPPING_TEMPLATE)
        child_incoming_node = node.find("IncomingMapping")
        child_incoming_node.text = mapping_node.address
        return node

    @staticmethod
    def _build_resource_child_nodes(node, resource):
        """
        Build resource nodes for children recursively
        :param resource:
        :type resource: cloudshell.layer_one.core.response.entities.base.ResourceInfo
        :param node: 
        :type node: xml.etree.ElementTree.Element
        """
        if len(resource.child_resources) > 0:
            child_resources_node = node.find('ChildResources')
            for child_resource in resource.child_resources.values():
                child_node = ResourceInfoBuilder._build_resource_node(child_resource)
                child_resources_node.append(child_node)
                ResourceInfoBuilder._build_resource_child_nodes(child_node, child_resource)

    @staticmethod
    def build_resource_info_nodes(base_resource):
        """
        Build tree of xml nodes for resource tree
        :param base_resource:
        :type base_resource: cloudshell.layer_one.core.response.entities.base.ResourceInfo
        :return:
        :type: xml.etree.ElementTree.Element
        """
        resource_node = ResourceInfoBuilder._build_resource_node(base_resource)
        ResourceInfoBuilder._build_resource_child_nodes(resource_node, base_resource)
        return resource_node
