class EntityValidator(object):

    @staticmethod
    def validate_id_for_name_template(resource_id):
        resource_id = str(resource_id)
        if not resource_id.isdigit() or len(resource_id) > 1:
            return resource_id
        else:
            return '0' + resource_id
