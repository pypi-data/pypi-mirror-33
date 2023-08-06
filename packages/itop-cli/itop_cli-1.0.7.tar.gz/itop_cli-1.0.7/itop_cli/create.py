"""
Utility to create objects.
"""
class Create:
    """
    Utility to create objects.
    """
    def __init__(self, itop, class_name, fields):
        self.itop = itop
        self.class_name = class_name
        if fields:
            self.fields = {}
            for field in fields:
                elements = field.split("=", 1)
                self.fields[elements[0]] = elements[1]

    def create(self):
        """
        Execute the creation.
        :return: None
        """
        try:
            response = self.itop.create(self.class_name, **self.fields)
            if response['code'] == 0 and response['message'] is None:
                print("Created object {}".format(list(response['objects'].keys())[0]))
            else:
                raise RuntimeError("Error creating {class_name} : {message}".format(class_name = self.class_name, message = response['message']))
        except IOError as exception:
            raise RuntimeError(str(exception))


def create(itop, class_name, fields):
    """
    Creates an object.
    :param itop:  itop connection
    :param class_name: class of the object to create
    :param fields: content of the object
    :return:
    """
    Create(itop, class_name, fields).create()
