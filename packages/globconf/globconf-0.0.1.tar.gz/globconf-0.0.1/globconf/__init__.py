name = 'globconf'
import configparser

"""
global/singleton config object to be uses across modules
"""
config = configparser.ConfigParser()
config.read('config.ini')
