"""
Utility to export objects.
"""


class Export:
    """
    Utility to export objects.
    """

    def __init__(self, itop, class_name, query=None, output_fields="*"):
        self.itop = itop
        self.class_name = class_name
        self.output_fields = output_fields
        if query is None or query == "":
            self.query = "SELECT " + class_name
        else:
            self.query = query

    def get(self):
        """
        Gets the objects data
        :return: JSON data as string
        """
        try:
            data = self.itop.get(self.class_name, self.query, self.output_fields)
            if data['code'] != 0:
                exit(data['message'])
            found = data['message'].split(" ")[1]
            if found == "0":
                exit("No object found for {}, i won't continue".format(self.query))
            else:
                return list(data["objects"].values())
        except IOError as exception:
            exit(str(exception))


def export_data(itop, class_name, query=None, output_fields="*"):
    """
    Exports data
    :param itop: itop connection
    :param class_name: class of the objects to export
    :param query: OQL query
    :param output_fields: list of fields to display
    :return: objects found; if no query provided, it will return all objects of the class
    """
    return Export(itop, class_name, query, output_fields).get()
