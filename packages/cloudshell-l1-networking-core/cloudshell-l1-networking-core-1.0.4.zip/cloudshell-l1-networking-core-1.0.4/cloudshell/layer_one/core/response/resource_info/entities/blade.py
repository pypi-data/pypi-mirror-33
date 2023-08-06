#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.layer_one.core.response.resource_info.entities.attributes import StringAttribute
from cloudshell.layer_one.core.response.resource_info.entities.base import ResourceInfo
from cloudshell.layer_one.core.response.resource_info.entities.validators import EntityValidator


class Blade(ResourceInfo):
    """Blade resource entity"""
    NAME_TEMPLATE = 'Blade {}'
    FAMILY_NAME = 'L1 Switch Blade'
    MODEL_NAME = 'Generic L1 Module'

    def __init__(self, resource_id, model_name=None, serial_number='NA'):
        model_name = model_name or self.MODEL_NAME
        name = self.NAME_TEMPLATE.format(EntityValidator.validate_id_for_name_template(resource_id))
        super(Blade, self).__init__(resource_id, name, self.FAMILY_NAME, model_name, serial_number)

    def set_model_name(self, value):
        if value:
            self.attributes.append(StringAttribute('Model Name', value))

    def set_serial_number(self, value):
        if value:
            self.attributes.append(StringAttribute('Serial Number', value))
