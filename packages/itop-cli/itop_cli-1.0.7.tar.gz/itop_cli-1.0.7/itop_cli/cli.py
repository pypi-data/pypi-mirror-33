#!/usr/bin/env python
"""
  Usage:
    itop delete <class> <query> (--env=<env>|--config=<config>)
    itop export <class> [<query>] [--output_fields=<output_fields>] (--env=<env>|--config=<config>) [--pretty]
    itop import <class> --input=<input_file> [--search_keys=<search_keys>] (--env=<env>|--config=<config>)
    itop create <class> [FIELDS]... (--env=<env>|--config=<config>)
    itop update <class> <search> [FIELDS]... (--env=<env>|--config=<config>)
    itop -h | --help | --version

  Arguments:
    FIELDS                         Key value pairs. Ex : "description=Ceci est une description". If not overridden, the script will use the org_id of the config file
    <query>                        OQL query.
    <search>                       Simple search element. "key=value" format

  Options:
    -e <env> --env=<env>                            Will search ~/.itop/<venv>.json as configuration file
    -c <config> --config=<config>                   Path to config file
    -s <search_keys> --search_keys=<search_keys>    Key(s) to search objects, comma separated [default: name]
    -f <output_fields> --output_fields=<output_fields>     Filed(s) to export, comma separated
    -i <input_file> --input=<input_file>            File to use for data input
    -p --pretty                                     Prettify JSON output

  Examples:
    itop delete Person 'SELECT Person WHERE status="inactive"' --env=dev
    itop export SynchroDataSource --env=dev
    itop export Server "SELECT Server WHERE name LIKE 'SRVTEST'" --env=dev -f name
    itop import SynchroDataSource --input=/tmp/out.json --search_keys=database_table_name
    itop create Server "name=SRVTEST" "description=Serveur de test" --env=dev
    itop update Server "name=SRVTEST" "description=Serveur de prod" --env=dev
    itop update Server "name=SRVTEST" "description=Serveur de prod" "brand_id=SELECT Brand WHERE name='Altiris'" --env=dev
"""

from os.path import join, expanduser

from json import load, dumps
from docopt import docopt

import itopy

from . import import_data, export_data, delete, create, update


def org_id(itop, org_name):
    """
    Search the id of an organization
    :param itop: itop connection
    :param org_name: name of the organization to search
    :return:
    """
    response = itop.get('Organization', 'SELECT Organization WHERE name = "%s"' % org_name)
    if "code" not in response:
        raise BaseException(response)
    if response['code'] != 0 and response['message'] != 'Found: 1':
        exit("Organization '{}' not found".format(org_name))
    code = list(response['objects'].values())[0]['key']
    return code


def main_itop():
    """
    Main function
    :return: None
    """
    arguments = docopt(__doc__, version='0.1')

    if arguments["--config"] is not None:
        conf_path = arguments["<config>"]

    if arguments["--env"] is not None:
        conf_path = join(expanduser('~'), ".itop", arguments["--env"] + ".json")

    try:
        conf = load(open(conf_path, "r"))
    except IOError as exception:
        exit(str(exception))

    if ("url" not in conf) \
            or ("version" not in conf) \
            or ("user" not in conf)\
            or ("password" not in conf)\
            or ("org_name" not in conf):
        exit("Wrong config file format")

    itop = itopy.Api()
    itop.connect(conf["url"], conf["version"], conf["user"], conf["password"])

    # Connection test. This value will also be used for creations
    try:
        main_org_id = org_id(itop, conf["org_name"])
    except BaseException as exception:
        exit(str(exception))

    try:
        if arguments["delete"]:
            delete(itop, arguments["<class>"], arguments["<query>"], )

        if arguments["export"]:
            export = export_data(itop, arguments["<class>"], arguments["<query>"], arguments["--output_fields"])
            if arguments["--pretty"]:
                print(dumps(export, sort_keys=True, indent=4, separators=(',', ': ')))
            else:
                print(dumps(export))

        if arguments["import"]:
            data = open(arguments["--input"], "r")
            import_data(itop, arguments["<class>"], data, arguments["--search_keys"])

        if arguments["create"]:
            fields = arguments["FIELDS"]
            if "org_id" not in fields:
                fields.append("org_id=%s" % main_org_id)
            create(itop, arguments["<class>"], arguments["FIELDS"])

        if arguments["update"]:
            fields = arguments["FIELDS"]
            update(itop, arguments["<class>"], arguments["<search>"], arguments["FIELDS"])

    except Exception as exception:
        exit("{} : {}".format(type(exception), str(exception)))
