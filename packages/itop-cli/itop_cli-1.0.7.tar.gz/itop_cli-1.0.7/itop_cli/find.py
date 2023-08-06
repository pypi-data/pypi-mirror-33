def find(itop, class_name, query):
    """
    Finds elements to delete
    :param itop: itop connection
    :param class_name: name of the class of the objects to delete
    :param query: query to filter objects to delete
    :return: None
    """
    elements = itop.get(class_name, query, output_fields="friendlyname")
    found = elements['message'].split(" ")[1]
    if found == "0":
        return None
    else:
        return list(elements['objects'].items())