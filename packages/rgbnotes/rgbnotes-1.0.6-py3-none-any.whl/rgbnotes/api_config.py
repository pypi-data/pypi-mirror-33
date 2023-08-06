import os
import ConfigParser


CONFIG_FILE = 'rgb_api.conf'


class RGB_ConfigError(Exception):
    '''Config error base class'''
    pass


def get_config():
    parser = get_config_path()[-1]
    return parser


def get_config_path():
    # /currentdir/rgb_api.conf, /home/username/rgb_api.conf, /etc/rgb_api.conf
    base_dir = '.' if __name__ == '__main__' else os.path.dirname(__file__)
    config_paths = [os.path.join(os.path.abspath(base_dir), CONFIG_FILE),
                    os.path.expanduser('~/{}'.format(CONFIG_FILE)),
                    '/etc/{}'.format(CONFIG_FILE)]

    parser = ConfigParser.SafeConfigParser()
    config = parser.read(config_paths)
    if not config:
        raise RGB_ConfigError('config file not found. ' \
                              'Searched %s' % (config_paths))
    return (config, parser)


def write_data(section, keyword, data):
    config, parser = get_config_path()
    try:
        parser.add_section(section)
    except ConfigParser.DuplicateSectionError:
        pass
    parser.set(section, keyword, data)

    with open(config[-1], 'wb') as configfile:
        parser.write(configfile)


def read_data(section, keyword):
    config = get_config()
    try:
        return config.get(section, keyword)
    except:
        return None
