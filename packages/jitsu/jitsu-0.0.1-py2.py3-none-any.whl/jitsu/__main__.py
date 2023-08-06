import argparse
import os
import sys

import jinja2
from jinja2 import Environment, FileSystemLoader
import yaml


def generate(data_dir='data', templates_dir='templates',
             escape=None, res='_dist'):
    """
    Generate content after rendering the data.

    :param data_dir:
        Directory to use for finding data files.
    :param templates_dir:
        Directory to lookup templates into.
    :param escape:
        List of extensions to escape from considering as templates.
    :param res:
        Directory to store the generated results to:
    """

    curr_path = os.getcwd()
    data_dir = os.path.join(curr_path, 'data')
    templates_dir = os.path.join(curr_path, 'templates')

    env = Environment(loader=FileSystemLoader(templates_dir), )


    if os.path.exists(data_dir):
        for entry in os.scandir(data_dir):
            if not entry.is_file():
                pass

            with open(entry.path) as f:
                data = yaml.load(f)

            jitsu = data.pop('jitsu')

            if 'template' not in jitsu:
                print('Template for {} not found, skipping...')
                continue

            try:
                template = env.get_template(jitsu['template'])
            except jinja2.TemplateNotFound:
                print('Template {} required for {} does not exist, skipping...'.format(
                    jitsu['template'], entry.path,
                    env.join_path(jitsu['template'], None)
                ))
                continue

            file_name_without_extension = '.'.join(entry.path.split('/')[-1].split('.')[:-1])

            if not os.path.exists('_dist'):
                os.mkdir('_dist')

            with open('_dist/' + file_name_without_extension + '.' +
                      jitsu['generates'], 'w') as output:
                print('generating {}...'.format(file_name_without_extension + '.' + jitsu['generates']))
                output.write(template.render(**data))


def main(args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-dir', help='data directory', default='data')
    parser.add_argument('-t', '--templates-dir', help='templates directory', default='templates')
    parser.add_argument('-r', '--results-dir',
                        help='Directory to store rendered templates to.',
                        default='_dist')
    parser.add_argument('-I', '--ignore-extensions',
                        help='Files with extensions to ignore from templates directory.',
                        default=[])

    args = parser.parse_args(args)

    generate(args.data_dir, args.templates_dir, args.ignore_extensions,
             args.results_dir)

if __name__ == '__main__':  # pragma: no cover
    main()
