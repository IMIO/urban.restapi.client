# -*- coding: utf-8 -*-


class Contact:

    def __init__(self, type, line):
        """ """
        self.type = type
        self.personTitle = line['Titre']
        self.name1 = line['Nom']
        self.name2 = line['Prenom']
