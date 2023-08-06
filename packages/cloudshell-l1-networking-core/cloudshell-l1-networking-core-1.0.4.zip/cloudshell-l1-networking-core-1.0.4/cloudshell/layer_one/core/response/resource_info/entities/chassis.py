#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.layer_one.core.response.resource_info.entities.attributes import StringAttribute
from cloudshell.layer_one.core.response.resource_info.entities.base import ResourceInfo
from cloudshell.layer_one.core.response.resource_info.entities.validators import EntityValidator


class Chassis(ResourceInfo):
    """
    Chassis resource entity
    """
    NAME_TEMPLATE = 'Chassis {}'
    FAMILY_NAME = 'L1 Switch'

    def __init__(self, resource_id, address, model_name, serial_number=None):
        self._address = address
        name = self.NAME_TEMPLATE.format(EntityValidator.validate_id_for_name_template(resource_id))
        family_name = self.FAMILY_NAME
        serial_number = serial_number or 'NA'
        super(Chassis, self).__init__(resource_id, name, family_name, model_name, serial_number)

    @property
    def address(self):
        return self._address

    def set_model_name(self, value):
        if value:
            self.attributes.append(StringAttribute('Model Name', value))

    def set_serial_number(self, value):
        if value:
            self.attributes.append(StringAttribute('Serial Number', value))

    def set_os_version(self, value):
        if value:
            self.attributes.append(StringAttribute('OS Version', value))
