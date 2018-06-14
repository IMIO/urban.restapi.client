# -*- coding: utf-8 -*-

import os

from urban.restapi.client.type.contact import Contact


def format_path(path):
    if os.path.exists(path):
        return path

    return os.path.join(os.getcwd(), path)


def line_to_contact(type, line):
    return Contact(type, line)
