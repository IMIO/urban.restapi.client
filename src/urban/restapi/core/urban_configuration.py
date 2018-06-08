# -*- coding: utf-8 -*-

from urban.restapi.core import utils

import requests
import configparser


class Configuration:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config

        response = requests.post('http://localhost:8081/restapi/@login',
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                 data='{"login": "admin", "password": "admin"}')

        # print(response.status_code)


def main():
    """ """
