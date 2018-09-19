# -*- coding: utf-8 -*-


# from urban.restapi.client import utils
from urban.restapi.client.utils import format_path

import argparse
import configparser
import csv
import requests


RESPONSE_SUCCESS = 200
RESPONSE_CREATED_SUCCESS = 201

VALUES_MAPS = {
    'title_map': {
        'Monsieur': 'mister',
        'M.': 'mister',
        'Messieurs': 'misters',
        'Madame': 'madam',
        'Mesdames': 'ladies',
        'Mademoiselle': 'miss',
        'M. et Mme': 'madam_and_mister',
        'Monsieur et Madame': 'madam_and_mister',
        'Maître': 'master',
    },

    'country_map': {
        'Belgique': 'belgium',
        'Allemagne': 'germany',
        'France': 'france',
        'Pays-Bas': 'netherlands',
    },
}


class ImportContacts:

    def __init__(self, config_file, portal_type, csv_file, path_type, limit):
        config = configparser.ConfigParser()
        config_file = format_path(config_file)
        config.read(config_file)
        self.config = config
        self.portal_type = portal_type
        self.csv_file = csv_file
        self.path_type = path_type
        self.limit = limit
        self.plone_site = ('{host}/{site}'.format(**config._sections['plone']))
        self.host = config._sections['plone']['host']

        response = requests.post(self.host + '/@login',
                                 headers={'Accept': 'application/json',
                                          'Content-Type': "application/json;charset=utf-8"},
                                 data='{"login": "%s", "password": "%s"}' % (config._sections['plone']['user'],
                                                                             config._sections['plone']['password']))
        if response.status_code == RESPONSE_SUCCESS:
            self.token = response.json()['token']

            self.head = {'Accept': 'application/json', 'Content-Type': 'application/json',
                         'Authorization': 'Bearer {}'.format(self.token)}
        else:
            print(response.status_code)

    def execute(self):
        title_mapping = VALUES_MAPS.get('title_map')
        country_mapping = VALUES_MAPS.get('country_map')
        with open(self.csv_file, 'r', 1024, 'utf-8') as file:
            reader = csv.DictReader(file, quoting=csv.QUOTE_NONE, **self.config._sections['csv'])
            for idx, line in enumerate(reader):
                if self.limit and (self.limit - 1) < idx:
                    print("Specified limit reached: %i" % self.limit)
                    break
                if self.portal_type == 'Architect':
                    data = '{"@type": "%s", ' \
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
                           % (self.portal_type,
                              line['Nom'],
                              line['Prenom'],
                              line['Bureau'],
                              line['Rue+No'],
                              line['CP'],
                              line['Gsm'],
                              line['E-mail'],
                              line['Fax'],
                              line['Ville'],
                              country_mapping.get(line['Pays']),
                              line['Téléphone'],
                              title_mapping.get(line['Titre']),
                              )
                elif self.portal_type == 'Notary':
                    data = '{"@type": "%s", ' \
                           '"name1": "%s", ' \
                           '"name2": "%s", ' \
                           '"street": "%s", ' \
                           '"zipcode": "%s", ' \
                           '"fax": "%s", ' \
                           '"city": "%s", '\
                           '"phone": "%s"}' \
                           % (self.portal_type,
                              line['Nom'],
                              line['Prenom'],
                              line['Adresse1'],
                              line['Code_postal'],
                              line['Fax'],
                              line['Ville'],
                              line['Telephone'],
                              )
                elif self.portal_type == 'Geometrician':
                    data = '{"@type": "%s", ' \
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
                           % (self.portal_type,
                              line['Nom'],
                              line['Prénom'],
                              line['Bureau'],
                              line['Rue+No'],
                              line['CP'],
                              line['Gsm'],
                              line['E-mail'],
                              line['Fax'],
                              line['Ville'],
                              country_mapping.get(line['Pays']),
                              line['Téléphone'],
                              title_mapping.get(line['Titre']),
                              )
                data = data.encode("utf-8")
                response = requests.post(self.host + '/urban/%s' % self.path_type,
                                         headers=self.head,
                                         data=data)
                if response.status_code != RESPONSE_CREATED_SUCCESS:
                    print(response.status_code)
                    break


def main():
    """ """

    # example
    # bin/import_contacts configuration_example.cfg Geometrician geometricians var/urban/geo.csv
    # bin/import_contacts configuration_example.cfg Architect architects var/urban/architects.csv --limit 2
    # bin/import_contacts configuration_example.cfg Notary notaries var/urban/notaires.csv --limit 100
    parser = argparse.ArgumentParser(description="Import contact from csv file")
    parser.add_argument("config_file", type=str, help="path to the config")
    parser.add_argument("portal_type", type=str, help="contact portal type")
    parser.add_argument("path_type", type=str, help="path to the contacts")
    parser.add_argument("csv_file", type=str, help="path to the csv input")
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()
    ImportContacts(args.config_file, args.portal_type, args.csv_file, args.path_type, args.limit).execute()
