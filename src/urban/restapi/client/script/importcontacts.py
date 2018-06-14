# -*- coding: utf-8 -*-


from urban.restapi.client import utils

import argparse
import configparser
import csv
import requests

RESPONSE_SUCCESS = 200
RESPONSE_CREATED_SUCCESS = 201

VALUES_MAPS = {
    'title_map': {
        'Monsieur': 'mister',
        'Messieurs': 'misters',
        'Madame': 'madam',
        'Mesdames': 'ladies',
        'Mademoiselle': 'miss',
        'M. et Mme': 'madam_and_mister',
    },

    'country_map': {
        'Belgique': 'belgium',
        'Allemagne': 'germany',
        'France': 'france',
        'Pays-Bas': 'netherlands',
    },
}


class ImportContacts:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        response = requests.post('http://localhost:8081/restapi/@login',
                                 headers={'Accept': 'application/json', 'Content-Type': "application/json; "
                                                                                        "charset=utf-8"},
                                 data='{"login": "admin", "password": "admin"}')
        if response.status_code == RESPONSE_SUCCESS:
            self.token = response.json()['token']

            self.head = {'Accept': 'application/json', 'Content-Type': 'application/json',
                         'Authorization': 'Bearer {}'.format(self.token)}
        else:
            print(response.status_code)

    def execute(self):

        title_mapping = VALUES_MAPS.get('title_map')
        with open('var/urban/blc_architects.csv', 'r', 1024, 'utf-8') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)

            for idx, line in enumerate(reader):
                data = '{"@type": "Architect", ' \
                       '"name1": "%s", ' \
                       '"name2": "%s", ' \
                       '"society": "%s", ' \
                       '"street": "%s", ' \
                       '"zipcode": "%s", ' \
                       '"gsm": "%s", ' \
                       '"email": "%s", ' \
                       '"fax": "%s", ' \
                       '"city": "%s", '\
                       '"country": "%s", '\
                       '"phone": "%s", ' \
                       '"personTitle": "%s"}'\
                       % (line['Nom'],
                          line['Prenom'],
                          line['Societe'],
                          line['Rue et Numero'],
                          line['Code postal'],
                          line['Email'],
                          line['Gsm'],
                          line['Fax'],
                          line['Localite'],
                          title_mapping.get(line['Pays']),
                          line['Telephone'],
                          title_mapping.get(line['Titre']),
                          )
                data = data.encode("utf-8")

                response = requests.post('http://localhost:8081/restapi/urban/architects/',
                                         headers=self.head,
                                         data=data)

                if response.status_code != RESPONSE_CREATED_SUCCESS:
                    print(response.status_code)
                    break


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import contact from Architects csv file')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()
    ImportContacts(args.config_file).execute()
