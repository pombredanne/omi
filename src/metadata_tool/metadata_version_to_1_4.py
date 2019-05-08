#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import datetime
from collections import OrderedDict

def file_to_string(path):
    """Extracts the text content of a file and returns it

    Parameters
    ----------
    path: str
        The path to the file.

    Returns
    -------
    filestring: str
        The contents of the input file.
    """

    filestring = ""
    with open(path, "r") as myfile:
        filestring = myfile.read()
    return filestring

def is_json(myjson):
    """Checks the validity of a JSON string

    Parameters
    ----------
    myjson: str
        The JSON string to be checked.

    Returns
    -------
    bool
        True if valid JSON, False otherwise.
    """

    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

def is_1_3_metastring(json_string):
    """Checks string conformity to OEP Metadata Standard Version 1.3

    Parameters
    ----------
    json_string: str
        The JSON string to be checked.

    Returns
    -------
    bool
        True if valid, Raises Exception otherwise.
    """

    keys = ["title", "description", "language", "spatial", "temporal", "sources", "license", "contributors", "resources", "metadata_version"]
    subkeys_spatial = ["location", "extent", "resolution"]
    subkeys_temporal = ["reference_date", "start", "end", "resolution"]
    subkeys_license = ["id", "name", "version", "url", "instruction", "copyright"]
    object_subkeys = {"spatial": subkeys_spatial, "temporal": subkeys_temporal, "license": subkeys_license}
    subkeys_sources = ["name", "description", "url", "license", "copyright"] # in list of objects
    subkeys_contributors = ["name", "email", "date", "comment"] # in list of objects
    subkeys_resources = ["name", "format", "fields"] # in list of objects
    list_subkeys = {"sources": subkeys_sources, "contributors": subkeys_contributors, "resources": subkeys_resources}
    subkeys_resources_fields = ["name", "description", "unit"] # in list of objects

    try:
        # check if all top level keys are present
        for i in keys:
            if not i in json_string.keys():
                raise Exception('The String did not contain the key "{0}"'.format(i))
        # check for all keys in second level objects
        for key in object_subkeys:
            for subkey in object_subkeys[key]:
                if not subkey in json_string[key]:
                    raise Exception('The "{0}" object did not contain a "{1}" key'.format(key, subkey))
        # check for all objects in lists if they contain all required keys
        for key in list_subkeys:
            for list_element in json_string[key]:
                for subkey in list_subkeys[key]:
                    if not subkey in list_element:
                        raise Exception('An object in "{0}" is missing a "{1}" key'.format(key, subkey))
    except Exception as error:
        print("The input String does not conform to metadatastring version 1.3 standard")
        print(error)
    return True

# TODO make function check all subkeys as well
def has_rogue_keys(json_string):
    """Checks all keys if they are part of the metadata specification. Gives warnings if not.

    Parameters
    ----------
    json_string: str
        The JSON string to be checked.

    Returns
    -------
    """

    keys = []
    for i in json_string:
        keys.append(i)
    allowed_keys = ["title", "description", "language", "spatial", "temporal", "sources", "license", "contributors", "resources", "metadata_version"]
    for j in keys:
        if not j in allowed_keys:
            print('Warning: "{0}" is not among the allowed keys'.format(j))

def json_extraction(sql_input, json_output = 'old_json.json'):
    """Extracts the json string from an existing COMMENT ON TABLE query file to an output file.

    Parameters
    ----------
    sql_input: str
        The sql input file.
    json_output: str
        the extracted json output file.

    Returns
    -------
    json_output: str
        The name of the extracted output file.
    """

    # Open input and output file. The output with r+ -option (read-write)
    input_file = open(sql_input, 'r')
    output_file = open(json_output, 'w')

    # list that include lines of v2 and v3
    input_file_lines = input_file.readlines()

    # TODO write function to check input string on correct structure
    json_start = 1
    if not json_start:
        raise RuntimeError('The metadata input file does not match the requisite structure.')

    # copy the json from the input_file to output_file
    output_file.write("{")
    for index_l, line in enumerate(input_file_lines[json_start:]):
        if index_l < len(input_file_lines[json_start:]):
            output_file.write(line)
        else:
            output_file.write(line[:-3])

    # closing files
    input_file.close()
    output_file.close()

    return json_output

def json_conversion(tablename, username, user_email, json_old_input, json_new_output = 'json_new.json'):
    """Converts a pure json metadata file to a new json file structure

    Parameters
    ----------
    tablename: str
        The tablename the metadata corresponds to.
    username: str
        The name of the contributor for the 'contributors' list.
    user_email: str
        The email address of the contributor for the 'contributors' list.
    json_old_input: str
        The json input filename that is going to be converted.
    json_new_output: str
        The new json filename that is gonna be created.

    Returns
    -------
    json_new_output: str
        The filename of the created json file.
    """

    # get current time
    now = datetime.datetime.now()

    # open json file
    f = open(json_old_input)

    # transforming it to python dict with package json
    json_old = json.load(f)

    # In the following a new structure is set. The yet implemented version is for metadata v1.2 to v1.3.

    # To keep the sequence an Ordered dict is used
    d = OrderedDict()

    d['name'] = ''
    d['title'] = json_old['title']
    d['id'] = ''
    d['description'] = json_old['description']
    d['language'] = json_old['language']
    d['keywords'] = ['']
    d['publicationDate'] = ''

    # context section
    d_context = OrderedDict()
    d['context'] = d_context
    d_context['homepage'] = ''
    d_context['documentation'] = ''
    d_context['sourceCode'] = ''
    d_context['contact'] = ''
    d_context['grantNo'] = ''

    # filling the spatial section
    d_spatial = OrderedDict()
    d['spatial'] = d_spatial
    d_spatial['location'] = ''
    #d_spatial['extend'] = json_old['spatial'][0]['extend']
    d_spatial['extent'] = json_old['spatial']['extent']
    d_spatial['resolution'] = json_old['spatial']['resolution']

    # filling the temporal section
    d_temporal = OrderedDict()
    d['temporal'] = d_temporal
    d_temporal['referenceDate'] = json_old['temporal']['reference_date']
    d_temporal['start'] = ''
    d_temporal['end'] = ''
    d_temporal['resolution'] = ''
    d_temporal['timestamp'] = ''

    # filling the source section
    d['sources'] = []
    for i in range(len(json_old['sources'])):
        d['sources'].append(OrderedDict())
        d['sources'][i]['title'] = json_old['sources'][i]['name']
        d['sources'][i]['description'] = json_old['sources'][i]['description']
        d['sources'][i]['path'] = json_old['sources'][i]['url']
        d['sources'][i]['license'] = ''
        d['sources'][i]['copyright'] = json_old['sources'][i]['copyright']

    # filling the license section
    d_licenses = OrderedDict()
    d['licenses'] = d_licenses
    d_licenses['name'] = json_old['license']['id']
    d_licenses['title'] = json_old['license']['name']
    d_licenses['path'] = json_old['license']['url']
    d_licenses['instruction'] = json_old['license']['instruction']
    d_licenses['attribution'] = json_old['license']['copyright']

    # filling the contributers section
    d['contributors'] = []
    for i in range(len(json_old['contributors'])):
        d['contributors'].append(OrderedDict())
        d['contributors'][i]['title'] = json_old['contributors'][i]['name']
        d['contributors'][i]['email'] = json_old['contributors'][i]['email']
        d['contributors'][i]['date'] = json_old['contributors'][i]['date']
        d['contributors'][i]['object'] = ''
        d['contributors'][i]['comment'] = json_old['contributors'][i]['comment']

    # extending with script-user information
    d['contributors'].append(OrderedDict())
    index = len(json_old['contributors'])
    d['contributors'][index]['name'] = '{}'.format(username)
    d['contributors'][index]['email'] = '{}'.format(user_email)
    d['contributors'][index]['date'] = '{}-{}-{}'.format(now.year,
                                                         now.month,
                                                         now.day)
    d['contributors'][index]['comment'] = 'Update metadata to v1.3 using metadata conversion tool'

    # filling the resources section
    d['resources'] = []
    #print(json_old['resources'][0]['fields'])
    for i in range(len(json_old['resources'])):
        d['resources'].append(OrderedDict())
        d['resources'][i]['profile'] = ''
        d['resources'][i]['name'] = '{}'.format(tablename)
        d['resources'][i]['path'] = ''
        d['resources'][i]['format'] = 'PostgreSQL'
        d['resources'][i]['encoding'] = ''
        d['resources'][i]['schema'] = []
        for j in range(len(json_old['resources'])):
            d['resources'][i]['schema'].append(OrderedDict())
            d['resources'][i]['schema'][j]['fields'] = []
            for k in range(len(json_old['resources'][i]['fields'])):
                d['resources'][i]['schema'][j]['fields'].append(OrderedDict())
                d['resources'][i]['schema'][j]['fields'][k]['name'] = json_old['resources'][i]['fields'][k]['name']
                d['resources'][i]['schema'][j]['fields'][k]['description'] = json_old['resources'][i]['fields'][k]['description']
                d['resources'][i]['schema'][j]['fields'][k]['type'] = ''
                d['resources'][i]['schema'][j]['fields'][k]['unit'] = json_old['resources'][i]['fields'][k]['unit']
            d['resources'][i]['schema'][j]['primaryKey'] = ''

    d_review = OrderedDict()
    d['review'] = d_review
    d_review['path'] = ''
    d_review['badge'] = ''

    d_metameta = OrderedDict()
    d['metaMetadata'] = d_metameta
    d_metameta['metadataVersion'] = ''
    d_metameta['metadataLicense'] = OrderedDict()
    d_metameta['metadataLicense']['name'] = ''
    d_metameta['metadataLicense']['title'] = ''
    d_metameta['metadataLicense']['path'] = ''

    d_comment = OrderedDict()
    d['_comment'] = d_comment
    d_comment['metadata'] = 'Metadata documentation and explanation (https://github.com/OpenEnergyPlatform/organisation/wiki/metadata)'
    d_comment['dates'] = 'Dates and time must follow the ISO8601 including time zone (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss±hh)'
    d_comment['units'] = 'Use a space between numbers and units (100 m)'
    d_comment['languages'] = 'Languages must follow the IETF (BCP47) format (en-GB, en-US, de-DE)'
    d_comment['licenses'] = 'License name must follow the SPDX License List (https://spdx.org/licenses/'
    d_comment['review'] = 'Following the OEP Data Review (https://github.com/OpenEnergyPlatform/data-preprocessing/wiki)'
    d_comment['none'] = 'If not applicable use (none)'


    # transforming back to json
    f = json.dumps(d, cls=MyJSONEncoder)

    fileout = open(json_new_output, 'w')
    fileout.write(f)
    fileout.close()

    return json_new_output

def metadata_creation(new_sql, tablename, new_json):
    """Creation of a new metadata sql-script by including the new json string

    Parameters
    ----------
    new_sql: str
        The filename of the new sql metadata script.
    tablename: str
        The name of the database table.
    new_json: str
        The json file that needs to be implemented in the new metadata script.

    Returns
    -------
    """

    json_file = open(new_json, 'r')
    json_file_lines = json_file.readlines()
    new_sql_file = open(new_sql, 'w')

    for line in json_file_lines:
        new_sql_file.write(line)

    json_file.close()
    new_sql_file.close()


def get_tablename(metadata_file):
    """Provides the tablename information from the metadata_file

    Parameters
    ----------
    metadata_file: str
        The metadata script from where the tablename is extracted from.

    Returns
    -------
    tablename: str
        returns the tablename.
    """

    return "get_tablename_placeholder"

class MyJSONEncoder(json.JSONEncoder):
    """This enconder sets up a structured oder of the json string when transforming it from a python dict

    """
    def __init__(self, *args, **kwargs):
        super(MyJSONEncoder, self).__init__(*args, **kwargs)
        self.current_indent = 0
        self.current_indent_str = ""

    def encode(self, o):
        # Special Processing for lists
        if isinstance(o, (list, tuple)):
            primitives_only = True
            for item in o:
                if isinstance(item, (list, tuple, dict)):
                    primitives_only = False
                    break
            output = []
            if primitives_only:
                for item in o:
                    output.append(json.dumps(item))
                return "[ " + ", ".join(output) + "  ]"
            else:
                self.current_indent += 2
                self.current_indent_str = "".join(
                    [" " for x in range(self.current_indent)])
                liste = []
                for item in o:
                    output = []
                    # This is performed if in the list is a dict
                    if isinstance(item, dict):
                        for key, value in item.items():
                            output.append(
                                json.dumps(
                                    key) + ": " + self.encode(value))

                        liste.append(
                            "\n" + 2 * self.current_indent_str + "{" + (",\n" + 2 * self.current_indent_str).join(
                                output) + "}")

                    else:
                        raise AssertionError(
                            'Only dicts in lists are properly structured. Please redefine it in the encode function.')
                        output.append(
                            self.current_indent_str + self.encode(item))
                        return "[\n" + ",".join(output) + "]"

                self.current_indent -= 2
                self.current_indent_str = "".join([" " for x in range(self.current_indent)])

            return "[" + ",".join(liste) + "]"

        elif isinstance(o, dict):
            output = []
            self.current_indent += 4
            self.current_indent_str = "".join(
                [" " for x in range(self.current_indent)])
            for key, value in o.items():
                output.append(self.current_indent_str + json.dumps(
                    key) + ": " + self.encode(value))
            self.current_indent -= 4
            self.current_indent_str = "".join(
                [" " for x in range(self.current_indent)])
            return "{\n" + ",\n".join(
                output) + "}"
        else:
            return json.dumps(o)

def metadata_conversion(old_sql, new_sql, user, user_email, only_endfiles = True):
    """ Conversion of an existing metadata file to a newer version by using the above functions.

    Parameters
    ----------

    old_sql: str
        The filename of the old sql file.
    new_sql: str
        The filename of the new sql file.
    user: str
        The name of the user for the 'contributors' section
    user_email: str
        The email address of the user.
    only_endfiles: bool
        If the json files that are created should be deleted in the end.

    Returns
    -------
    """

    # getting the json from a metadata-file
    json_old_string = json_extraction(old_sql, json_output = 'old_json.json')

    # getting the tablename from a metadata-file
    tablename = "bertbert"

    # converting the json string to the new version
    json_new_string = json_conversion(tablename, user, user_email, json_old_string, json_new_output = 'json_new.json')

    # creating the new metadata version
    metadata_creation(new_sql, tablename, json_new_string)

    # if only endfiles are wihsed the cache files are deleted
    if only_endfiles:
        os.remove(json_old_string)
        os.remove(json_new_string)


if __name__ == '__main__':
    if(len(sys.argv) < 2):
        print("usage: ")
        exit()
    path = sys.argv[1]
    filename, file_extension = os.path.splitext(path)
    outputfile = filename + "_converted" + file_extension
    if(len(sys.argv) >= 3):
        outputfile = sys.argv[2]
    try:
        json_string_in = file_to_string(path)
        if not is_json(json_string_in):
            raise Exception("\nInput File contains no valid json string.\nAborting\n")
        json_in = json.loads(json_string_in)
        is_1_3_metastring(json_in)
        has_rogue_keys(json_in)
        metadata_conversion(path, outputfile, "converter_script", "")
    except Exception as e:
        print(e)