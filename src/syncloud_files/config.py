from ConfigParser import ConfigParser
from os.path import join

BROWSER_CONFIG_NAME = 'files.cfg'


class BrowserConfig:

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.config_dir = join(data_dir, 'config')
        self.parser = ConfigParser()
        self.filename = join(self.config_dir, BROWSER_CONFIG_NAME)
        self.parser.read(self.filename)

    def www_root(self):
        return self.__get('www_root')

    def app_dir(self):
        return self.__get('app_dir')

    def config_dir(self):
        return self.__get('config_dir')

    def bin_dir(self):
        return self.__get('bin_dir')

    def get_web_secret_key(self):
        return self.__get('web_secret_key')

    def set_web_secret_key(self, value):
        return self.__set('web_secret_key', value)

    def get_browser_log(self):
        return self.__get('log_path')

    def __get(self, key):
        return self.parser.get('files', key)

    def __set(self, key, value):
        self.parser.set('platform', key, value)
        with open(self.filename, 'wb') as f:
            self.parser.write(f)