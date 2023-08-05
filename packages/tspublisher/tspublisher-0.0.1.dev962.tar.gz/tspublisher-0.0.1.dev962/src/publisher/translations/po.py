import os
import subprocess

from ruamel import yaml

from publisher import settings
from publisher.processing.utils.file import get_procedure_yaml_file
from publisher.translations.pot import build_translation_template
from publisher.utils import get_procedure_code


def get_procedure_locales():
    procedure_file = get_procedure_yaml_file()

    with open(procedure_file, 'rt') as y:
        yaml_obj = yaml.safe_load(y)

    return yaml_obj.get('locales', [])


def build_procedure_translation_template(procedure_code):
    pot_file = os.path.join(settings.TRANSLATIONS_CHECKOUT_DIRECTORY, '{0}.pot'.format(procedure_code))
    build_translation_template(pot_file)
    return pot_file


def merge_procedure_translation_files():
    procedure_code = get_procedure_code()
    locales = get_procedure_locales()

    template_file = build_procedure_translation_template(procedure_code)

    for locale in locales:
        output_file = os.path.join(settings.TRANSLATIONS_CHECKOUT_DIRECTORY,
                                   '{0}-{1}.po'.format(procedure_code, locale))

        if os.path.exists(output_file):
            subprocess.check_output(['msgmerge', '-U', '-q', '--previous', '--backup=off', output_file, template_file])
            print('Updated {0}'.format(output_file))
        else:
            subprocess.check_output(['msginit', '--l', locale, '--no-translator',
                                     '-i', template_file, '-o', output_file])

    os.remove(template_file)
