#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author: Olivier Watté <user>
# @Date:   2018-06-01T12:08:25-04:00
# @Email:  owatte@ipeos.com
# @Last modified by:   user
# @Last modified time: 2018-07-02T10:43:30-04:00
# @License: GPLv3
# @Copyright: IPEOS I-Solutions


"""Vigilance Meteo : French West Indies weather awareness level
Usage:
  vigimeteo AREA [--datastore=FILE_PATH] [--quiet] [--verbose]
  vigimeteo (-h |--help)
  vigimeteo (-v |--version)

Arguments:
  AREA        geographic area
              (gp=Guadeloupe, mq=Martinique, gf=Guyane, idn=Iles du Nord)

Options:
  -h --help                 Shows this help message and exit
  -v --version              Shows version number and exit
  --datastore=FILE_PATH     Datastore json file path (no datastore = no save)
  --quiet                   print less text
  --verbose                 print more text
"""

import uuid
import requests
from fake_useragent import UserAgent
import json
from docopt import docopt
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io

__all__ = ['meteoGP']
__version__ = "0.8.0"

gp = ('http://www.meteofrance.gp/previsions-meteo-antilles-guyane/'
      'temps-pour-les-prochaines-heures/guadeloupe/dept971')
# We hide the requests behind a random browser User Agent
ua = UserAgent()

headers = {'User-Agent': ua['google chrome'],  # ua.random,
           'Cache-Control': 'no-cache',
           'Pragma': 'no-cache',
           'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT'}

# headers = {'User-Agent': ua['google chrome']}


class meteoGP(object):
    AREAS = {
        'gp': ['Guadeloupe',
               ('http://'
                'www.meteofrance.gp/previsions-meteo-antilles-guyane/'
                'temps-pour-les-prochaines-heures/guadeloupe/dept971'),
               ('http://'
                'www.meteofrance.gp/integration/sim-portail/generated/'
                'integration/img/produits/pdf/suivi/'
                'bulletin_suivi_guadeloupe.pdf')],
        'mq': ['Martinique',
               ('http://'
                'www.meteofrance.gp/previsions-meteo-antilles-guyane/'
                'temps-pour-les-prochaines-heures/martinique/dept972'),
               ('http://'
                'www.meteofrance.gp/integration/sim-portail/generated/'
                'integration/img/produits/pdf/suivi/'
                'bulletin_suivi_martinique.pdf')],
        'idn': ['Iles du Nord',
                None,
                ('http://'
                 'www.meteofrance.gp/integration/sim-portail/generated/'
                 'integration/img/produits/pdf/suivi/'
                 'bulletin_suivi_iles_nord.pdf')],

        'gf': ['Guyane française',
               ('http://'
                'www.meteofrance.gp/previsions-meteo-antilles-guyane/'
                'temps-pour-les-prochaines-heures/guyane/dept973'),
               ('http://'
                'www.meteofrance.gp/integration/sim-portail/generated/'
                'integration/img/produits/pdf/suivi/'
                'bulletin_suivi_guyane.pdf')]
    }

    # levels = {COLOL_LEVEL: [ORDER, EXPLANATION]}
    LEVELS = {
        'vert': [
            'pas de vigilance particulière',
            ''
            ],
        'jaune': [
            'soyez attentifs',
            'des conditions de forte tempête tropicale ou un ouragan sont '
            'plausibles sur le territoire dans les 48 à 72h'
            ],
        'orange': [
            'préparez-vous',
            'des conditions de forte tempête ou d\'ouragan sont probables '
            'sur le territoire dans les 48h'
            ],
        'rouge': [
            'protégez-vous',
            'des conditions de forte tempête ou d\'ouragan sont probables '
            'sur le territoire dans 6 à 18h'
            ],
        'violet': [
            'confinez-vous',
            'des impacts majeurs associés à l\'ouragan sont attendus dans '
            '3 à 6h'
            ],
        'gris': [
            'restez prudent',
            'l\'ouragan s\'éloigne, mais tout danger n\'est pas écarté'
        ]
    }

    def __init__(self, area='gp', datastore=None):
        ''' init meteoGP crawler
        Args:
            area : str in 'gp', 'mq', 'idn'
        '''
        self.area = area
        self.datastore = datastore
        self.__vigilance = None
        self.__bulletin = {}
        self.__bulletin_previous = None
        self.__changed = None

    @property
    def bulletin(self):
        return self.__bulletin

    @property
    def bulletin_previous(self):
        return self.__bulletin_previous

    @bulletin_previous.setter
    def bulletin_previous(self, datastore):
        try:
            with open(datastore, 'r') as jf:
                self.__bulletin_previous = json.load(jf)
            jf.close()
        except OSError:
            self.__bulletin_previous = {}
            # self._save_data(self.__bulletin_previous)

    @property
    def changed(self):
        if self.bulletin == self.bulletin_previous:
            return False
        else:
            return True

    def save(self):
        with open(self.datastore, 'w') as jf:
            json.dump(self.bulletin, jf)
        jf.close()

    def scrap(self, codec='utf-8'):
        r = requests.get(self.AREAS[self.area][2],
                         headers=headers, stream=True)
        tmp_file = '/tmp/meteogp-{}.pdf'.format(uuid.uuid4())
        with open(tmp_file, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        fd.close()
        fp = open(tmp_file, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            content = retstr.getvalue()
        fp.close()
        os.remove(tmp_file)

        import re
        regex = re.compile(r'[\n\r\t]')
        content = regex.sub("", content)
        regex = re.compile(r'[\xa0]')
        content = regex.sub(" ", content)
        regex = re.compile(r'[\x0c]')
        content = regex.sub(".", content)

        for level in self.LEVELS:
            if not self.__vigilance:
                if level in content:
                    self.__vigilance = level
                    self.__bulletin = {
                        'area': self.AREAS[self.area][0],
                        'vigilance': level,
                        'content': content,
                        'instructions': self.LEVELS[level]
                    }
                    break


def main():
    arguments = docopt(__doc__,
                       version='Vigimeteo meteo.gp {}'.format(__version__))

    if arguments['--version']:
        print(__name__.__version__)
    elif arguments['AREA']:
        area = arguments['AREA'].lower()
        if arguments['--datastore']:
            datastore = arguments['--datastore']
        else:
            datastore = None

        vigilance = meteoGP(area=area, datastore=datastore)
        vigilance.scrap()
        if arguments['--quiet']:
            pass
        else:
            print(vigilance.bulletin['vigilance'])

        if arguments['--verbose']:
            print(vigilance.bulletin['area'])
            print(vigilance.bulletin['vigilance'])
            print('{} {}'.format(
                vigilance.bulletin['instructions'][0].capitalize(),
                vigilance.bulletin['instructions'][1].capitalize()))
            print(vigilance.bulletin['content'])

        if datastore:
            if vigilance.changed:
                vigilance.save()


if __name__ == '__main__':
    main()
