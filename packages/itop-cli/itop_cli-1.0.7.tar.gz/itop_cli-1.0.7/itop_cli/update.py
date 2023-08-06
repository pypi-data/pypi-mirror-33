"""
Utility to update objects.
"""


class Update:
    """
    Utility to update objects.
    """
    def __init__(self, itop, class_name, search, fields):
        self.itop = itop
        self.class_name = class_name
        s = Update.split(search)
        self.key = s[0]
        self.key_value = s[1]
        if fields:
            self.fields = Update.split_array(fields)

    def split_array(items):
        fields = {}
        for field in items:
            elements = Update.split(field)
            fields[elements[0]] = elements[1]
        return fields

    def split(field):
        elements = field.split("=", 1)
        return elements

    def update(self):
        """
        Execute the creation.
        :return: None
        """
        try:
            response = self.itop.update(self.class_name, self.key, self.key_value, **self.fields)
            if response['code'] == 0 and response['message'] is None:
                print("Updated object {}".format(list(response['objects'].keys())[0]))
            else:
                raise RuntimeError("Error updating {} : {}".format(self.class_name, response['message']))
        except IOError as exception:
            raise RuntimeError(str(exception))


def update(itop, class_name, search, fields):
    """
    Updates an object.
    :param itop:  itop connection
    :param class_name: class of the object to update
    :param search: simple search query in key=value format
    :param fields: content of the object
    :return:
    """
    Update(itop, class_name, search, fields).update()
