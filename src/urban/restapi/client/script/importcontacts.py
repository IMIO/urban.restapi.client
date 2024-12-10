# -*- coding: utf-8 -*-


# from urban.restapi.client import utils
from datetime import datetime

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
        'Monsieur l\'Architecte': 'mister',
        'M.': 'mister',
        'Messieurs': 'misters',
        'Madame': 'madam',
        'Madame l\'Architecte': 'madam',
        'Mesdames': 'ladies',
        'Mesdames, Messieurs': 'madam_and_mister',
        'Mademoiselle': 'madam',
        'Madame, Monsieur': 'madam_and_mister',
        'Monsieur et Madame': 'madam_and_mister',
        'la SPRL': '',
        'S.A.': '',
        'SPRL': '',
        'Association momentanée': '',
        "Bureau d\'étude": '',
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
        with open(self.csv_file, 'r', 1024, 'utf-8-sig') as file:
            reader = csv.DictReader(file, quoting=csv.QUOTE_ALL, **self.config._sections['csv'])
            for idx, line in enumerate(reader):
                if self.limit and (self.limit - 1) < idx:
                    print("Specified limit reached: %i" % self.limit)
                    break
                if self.portal_type == 'Architect':
                    data = '{"@type": "%s", ' \
                           '"name1": "%s", ' \
                           '"name2": "%s", ' \
                           '"street": "%s", ' \
                           '"zipcode": "%s", ' \
                           '"gsm": "%s", ' \
                           '"email": "%s", ' \
                           '"fax": "%s", ' \
                           '"city": "%s", '\
                           '"phone": "%s", ' \
                           '"personTitle": "%s"}'\
                           % (self.portal_type,
                              line['Nom'],
                              line['Prenom'],
                              line['Adresse'],
                              line['CodePostal'],
                              line['Gsm'],
                              line['Email'],
                              line['Fax'],
                              # line['Matricule'],
                              line['Localite'],
                              # country_mapping.get(line['Pays']),
                              line['Telephone'],
                              title_mapping.get(line['Civilite']),
                              )
                elif self.portal_type == 'Notary':
                    data = '{"@type": "%s", ' \
                           '"name1": "%s", ' \
                           '"name2": "%s", ' \
                           '"society": "%s", ' \
                           '"street": "%s", ' \
                           '"number": "%s", ' \
                           '"zipcode": "%s", ' \
                           '"fax": "%s", ' \
                           '"email": "%s", ' \
                           '"city": "%s", '\
                           '"phone": "%s", ' \
                           '"personTitle": "%s"}' \
                           % (self.portal_type,
                              line['Nom'],
                              line['Prenom'],
                              line['Bureau'],
                              line['Rue'],
                              line['No'],
                              line['CP'],
                              line['Fax'],
                              line['E-mail'],
                              line['Ville'],
                              line['Téléphone'],
                              title_mapping.get(line['Titre']),
                              )
                elif self.portal_type == 'Geometrician':
                    data = '{"@type": "%s", ' \
                           '"name1": "%s", ' \
                           '"name2": "%s", ' \
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
                              # line['Bureau'],
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
                elif self.portal_type == 'Parcelling':
                    # changes_description = {
                    #                          'data': "{0}{1}{2}".format("<p>", line['changesDescription'], "</p>"),
                    #                          'content-type': 'text/html'
                    #                       },
                    # number_of_parcels = int(line['NOMBRE DE LOTS'])
                    if not (line["DATE_DE_DE"] and line["DATE_STATU"]):
                        # ignore parcelling without date
                        continue
                    number_of_parcels = "0"
                    approval_date = self.inverte_day_month(line["DATE_DE_DE"])
                    authorization_date = self.inverte_day_month(line["DATE_STATU"])
                    data = '{"@type": "%s", ' \
                           '"label": "%s", ' \
                           '"subdividerName": "%s", ' \
                           '"authorizationDate": "%s", ' \
                           '"approvalDate": "%s", ' \
                           '"communalReference": "%s", ' \
                           '"numberOfParcels": "%s", ' \
                           '"DGO4Reference": "%s", ' \
                           '"changesDescription": "%s"}' \
                           % (self.portal_type,
                              line['CODE_ADMIN'],
                              line['CODE_ADMIN'],
                              authorization_date,
                              approval_date,
                              line['CODEUNIQUE'],
                              number_of_parcels,
                              line['CODE_ADMIN'],
                              "{0}{1}{2}".format("<p>", line['STATUT'], "</p>")
                              # "{0}{1}{2}".format("<p>", line['MODIFICATIONS DU LOTISSEMENT'], "</p>"),
                              )
                data = data.encode("utf-8")
                response = requests.post(self.host + '/urban/%s' % self.path_type,
                                         headers=self.head,
                                         data=data)
                if response.status_code != RESPONSE_CREATED_SUCCESS:
                    print(response.status_code)
                    print(response.text)
                    break

    def inverte_day_month(self, date):
        if date:
            try:
                obj_date = datetime.strptime(date.strip(), '%d/%m/%Y')
                return datetime.strftime(obj_date, '%Y-%m-%d')
            except ValueError:
                return


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
