from util import load_yaml
import os


p = os.path.abspath(os.path.dirname(__file__))
PALETS = load_yaml(os.path.join(p, 'palet.yml'))
onemorning = PALETS['onemorning']
