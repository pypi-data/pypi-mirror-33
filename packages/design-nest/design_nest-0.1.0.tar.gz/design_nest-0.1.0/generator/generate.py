import json
import os
import autopep8
from docformatter import format_code
from datetime import date
from jinja2 import Environment, PackageLoader
import pprint

from generator import generate_class, generate_group, generate_model
from settings import Settings

env = Environment(loader=PackageLoader('generator', 'templates'))


def clean_schema(schema):
    if not isinstance(schema, (dict, list)):
        return schema
    if isinstance(schema, list):
        return [clean_schema(v) for v in schema]
    return {k: clean_schema(v) for k, v in schema.items()
            if k not in {'memo', 'note', 'legacy_idd'}}


def create_file(group, objs):
    source_files = []
    for obj in objs:
        class_source = generate_class(obj)
        class_source = autopep8.fix_code(
            class_source,
            options=autopep8.parse_args(['--recursive', '--in-place', '--aggressive', '--aggressive', ''])
        )
        class_source = format_code(class_source)
        source_files.append(class_source)
    source = generate_group(group, source_files)

    with open(f"../design_nest/eplus_components/{group}.py", 'w') as f:
        f.write(source)


if __name__ == '__main__':
    
    with open(os.path.join(os.path.dirname(__file__), "schema", "eplus_8.9_schema.json")) as f:
        schema = json.load(f)
        schema = clean_schema(schema)

    objs = []
    # gplus_component file generation
    for group in Settings.groups:
        objects = []
        for obj in Settings.groups[group]:
            if obj in schema['properties']:
                d = {
                    'class_name': obj.replace(":", ""),
                    'eplus_name': obj,
                    'group': group,
                    'schema': schema['properties'][obj],
                    'fields': [prop for prop in schema['properties'][obj]['patternProperties']['.*']['properties']]
                }
                objects.append(d)
                objs.append(d)
        create_file(group, objects)

    helper_source = env.get_template('helper.py').render()
    with open("../design_nest/eplus_components/helper.py", 'w') as f:
        f.write(helper_source)

    # __init__.py file generation
    init_source = env.get_template('__init__.py').render(Settings.info)
    with open('../design_nest/__init__.py', 'w') as f:
        f.write(init_source)
