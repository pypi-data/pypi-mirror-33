import argparse


def get_nested_config_values(main_key, key, default):
    if main_key is None:
        return default
    if key in main_key:
        return main_key[key]
    else:
        return default


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')