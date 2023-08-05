import re
from collections import defaultdict

import polib
from ruamel import yaml

from publisher.git_handling.setup import call_command_and_print_exception
from publisher.utils import get_platform, find_command
from publisher.processing.utils.file import get_all_procedure_yaml_files


def ready_for_translations():
    if not (find_command('msgmerge') and find_command('msgfmt')):
        if get_platform().startswith('dar'):
            call_command_and_print_exception(['brew', 'install', 'gettext'], 'Could not brew install.')
            call_command_and_print_exception(['brew', 'link', '--force', 'gettext'], 'Could not brew link.')
        else:
            print('You must install gettext to continue with translations. \n'
                  'Please go to https://mlocati.github.io/articles/gettext-iconv-windows.html, \n'
                  'and follow the download instructions.')
            raise EnvironmentError
    return True


def build_translation_template(output_file):
    translatable_strings = get_translatable_strings()
    build_pot_file(translatable_strings, output_file)


def build_pot_file(strings, output_file):
    pot = polib.POFile()
    pot.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
    for string, locations in strings.items():
        entry = polib.POEntry(msgid=string, occurrences=locations)
        pot.append(entry)

    pot.save(fpath=output_file)


def get_translatable_strings():

    results = defaultdict(list)
    content_map = get_content_map()

    for yaml_file in get_all_procedure_yaml_files():
        with open(yaml_file, 'rb') as f:
            yaml_obj = yaml.load(f, Loader=yaml.RoundTripLoader)

        strings = extract_content(yaml_obj, content_map)
        for i in range(len(strings)):
            results[strings[i]].append((yaml_file, i))

    return results


def get_content_map():

    return {
        'name': str,
        'cta_text': str,
        'title': str,
        'subtitle': str,
        'sub_title': str,
        'text': str,
        'content': str,
        'answer': str,
        'desc': str,
        'numbered_list': list,
        'list': list,
        'choices': list,
    }


def extract_content(yaml_obj, content_map):
    results = []
    if isinstance(yaml_obj, list):
        for v in yaml_obj:
            results += extract_content(v, content_map)
    elif isinstance(yaml_obj, dict):
        for k, v in yaml_obj.items():
            mapped_type = content_map.get(k.lower())
            value_matches_type = mapped_type is not None and isinstance(v, mapped_type)
            if value_matches_type:
                string_list = v if mapped_type == list else [v]
                results += [s for s in string_list if is_translatable(s)]
            else:
                results += extract_content(v, content_map)

    return results


def is_translatable(s):
    is_not_empty = s is not None and s.strip() != ''
    return is_not_empty and (' ' in s or not re.search(r'[\d_]', s))
