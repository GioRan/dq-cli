from configparser import ConfigParser
import ast
from collections import defaultdict

config = ConfigParser()
config.optionxform = str
config.read('config.ini')

props = defaultdict(dict)
for cs in config.sections():
    for i in config.items(cs):
        props[cs][i[0]] = ast.literal_eval(i[1])