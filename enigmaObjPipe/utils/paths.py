import configparser

def read_objPipe_config(config_loc: str):
    '''Return config dictionary from config_loc'''
    config = configparser.ConfigParser()
    config.read(config_loc)

    return config
