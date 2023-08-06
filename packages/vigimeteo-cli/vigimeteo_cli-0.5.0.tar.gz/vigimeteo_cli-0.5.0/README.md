# Vigimeteo CLI

This module provides module and command line tool to retrieve official current
weathe awareness level (*vigilance météo*) for French West Indies areas
(Guadeloupe, Martinique, Saint Martin/Saint Barth and french Guyana) scraping
meteofrance.gp web site.

## Install

### From PIP

```bash
pip install vigimeteo-cli
```

### From source

```bash
git clone https://work.ipeos.com/gitlab/vigimeteo/vigimeteo-cli.git vigimeteo-cli
cd vigimeteo-cli
python setup.py install
```

## Usage

### Command Line Tool

```
Vigilance Meteo : French West Indies weather awareness level
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
```
#### Examples

Get current level for GP

```bash
$ vigimeteo gp
vert
```

Get current level, verbose mode
```bash
$ vigimeteo gp --verbose
Guadeloupe
vert
Pas de vigilance particulière
Département en vigilance verte.Pas de vigilance particulière.
```

Get current level, and store the record
```bash
$ vigimeteo gp --quiet --datastore=/data/vigimeteo.gp.json
```

### Python module
``` py
  >>> from vigimeteo_cli import meteoGP
  >>> vigilance = meteoGP(area='gp', datastore='/data/vigimeteo.gp.json')
  >>> vigilance.scrap()
  >>> print(vigilance.bulletin['vigilance'])
  >>> vigilance.save()
```

## Licence

This project is distributed under the [GPL V3 licence](LICENSE.md)
