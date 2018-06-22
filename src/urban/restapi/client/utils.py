# -*- coding: utf-8 -*-

from urban.restapi.client.type.contact import Contact

import os
import re


def format_path(path):
    if os.path.exists(path):
        return path

    return os.path.join(os.getcwd(), path)


def line_to_contact(type, line):
    return Contact(type, line)


def get_street_or_number(value, street_or_number):

    if street_or_number != 'street' and street_or_number != 'number':
        raise ValueError

    if street_or_number == 'number':
        return int(re.search(r'\d+', value).group())

    return ''.join([i for i in value if not i.isdigit()])
