#!/usr/bin/python
# -*- coding: utf-8 -*-


class ResourceInfo(object):
    """
    Basic resource info entity
    """

    def __init__(self, resource_id, name, family_name, model_name, serial_number, mapping=None):
        self.resource_id = str(resource_id)
        self.name = name
        self.family_name = family_name
        self.model_name = model_name
        self.serial_number = serial_number

        self.child_resources = {}
        self.attributes = []
        self._parent_resource = None
        self.mapping = mapping

    def set_parent_resource(self, parent_resource):
        """
        Set parent
        :param parent_resource:
        :type parent_resource: ResourceInfo
        :return: 
        """
        self._parent_resource = parent_resource
        parent_resource.child_resources[self.resource_id] = self

    @property
    def address(self):
        """
        Resource address
        :return: 
        """
        if self._parent_resource and self._parent_resource.address:
            address = '{0}/{1}'.format(self._parent_resource.address, self.resource_id)
        else:
            address = self.resource_id
        return address

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.address)

    def __repr__(self):
        return self.__str__()

    def add_mapping(self, resource_info):
        """
        Resource mapping, used for port resources
        :param resource_info: 
        :return: 
        """
        self.mapping = resource_info


class Attribute(object):
    """
    Basic attribute entity
    """
    NUMERIC = 'Numeric'
    STRING = 'String'
    BOOLEAN = 'Boolean'

    DEFAULT_VALUE = 'NA'

    def __init__(self, name, attr_type, value):
        self.name = name
        self.type = attr_type
        self.value = value

    def __str__(self):
        return '{0}: {1}'.format(self.name, self.value)

    def __repr__(self):
        return self.__str__()
