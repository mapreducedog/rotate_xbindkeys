'''
rotate_xbindkeys by mdp

convenience function for having xbindkeys "profiles"

'''
from __future__ import print_function
import json
import sys
import os
import glob
import itertools
__version__ = "1.0.0"

def print_version():
    '''print version of this program'''
    print("version: {}".format(__version__))

def notify(instr):
    os.system('''notify-send "{}"'''.format(instr))
def get_path():
    return os.path.abspath(os.path.dirname(sys.argv[0]))


def load_settings():
    path = get_path()
    with open( os.path.join(path, "settings.json"), 'r') as settingsfile:
        settings = json.load(settingsfile)
    return settings
def save_settings(settings):
    path = get_path()
    with open(os.path.join(path, "settings.json"), 'w') as settingsfile:
        json.dump(settings, settingsfile)

def get_next_pref_profile(next = True):
    get_conf_files = lambda : sorted(glob.glob(os.path.join(get_path(), "*.conf")))
    '''function for not repeating in activate_next_profile, activate_prev_profile'''
    settings = load_settings()
    targets = settings.get("profiles", []) or map(lambda x : os.path.splitext(os.path.split(x)[-1])[0], get_conf_files())
    next_index = settings.get("index", 0)
    print(targets)
    if settings.get("current", ''):
        next_index = targets.index(settings['current']) + (1 if next else -1)
    next_index %= len(targets)
    activate_named_profile(targets[next_index])

def activate_next_profile():
    '''activate the next profile'''
    get_next_pref_profile(next = True)

def activate_prev_profile():
    '''activate the previous profile'''
    get_next_pref_profile(next = False)

def activate_named_profile(profile_name):
    '''activate the named profile'''
    settings = load_settings()
    os.system("killall xbindkeys")
    assert(";" not in profile_name)
    filename = os.path.join(get_path(), profile_name) + ".conf"
    if ' ' in filename:
        filename = '"' + name + '"'
    return_value = os.system("xbindkeys --file {}".format(filename))
    if not return_value: #success
        notify("The new profile is {}".format(profile_name))
        settings['current'] = profile_name
        save_settings(settings)
    elif return_value == 65280:
        notify("could not find profile named {}.conf",format(profile_name))
    else:
        notify("xbindkeys returned error {}".format(return_value))
def print_help():
    '''print a summary of the program'''
    print(__doc__)

def check_option(short_option, long_option, return_arguments = False):
    if not short_option:
        short_option = '_______________________________________'
    if not long_option:
        long_option = '_______________________________________'
    for option in ["-" + short_option,
                   "--" + long_option]:
        if option in sys.argv:
            pos = sys.argv.index(option)
            if return_arguments:
                return list(itertools.takewhile(lambda x: not x.startswith("-"), sys.argv[pos + 1:]))
            else:
                return True
    for pos, string in enumerate(sys.argv[1:], 1):
        if string.startswith("-") and not string.startswith('--'):
            if short_option in string:
                if return_arguments:
                    return list(itertools.takewhile(lambda x: not x.startswith("-"), sys.argv[pos + 1:]))
                return True
    return [] if return_arguments else False

def main():
    for item in flags:
        short_option, long_option = item[1]
        return_arguments = item[2]
        return_value = check_option(short_option, long_option, return_arguments)
        if return_value:
            if return_arguments:
                item[0](return_value)
            else:
                item[0]()
    
flags = [(print_help, ('h', 'help'), False),
         (print_version, ('v', 'version'), False),
         (activate_next_profile, ('n', 'next'), False),
         (activate_prev_profile, ('p', 'prev'), False),
         ]
__doc__ += "\n".join(["-{1[0]}{3}, --{1[1]}{3}: {0.__doc__}".format(*(item + (" <args>" if item[-1] else "",))) for item in flags if any(item[1])]) 
if __name__ == '__main__':
    main()
