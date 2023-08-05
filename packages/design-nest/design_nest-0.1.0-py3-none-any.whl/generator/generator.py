from datetime import date
from jinja2 import Environment, PackageLoader
import pprint
env = Environment(loader=PackageLoader('generator', 'templates'))


def generate_class(obj):
    template = env.get_template('class.py')

    context = {"obj": obj}
    return template.render(context)


def generate_group(group_name, sources):
    template = env.get_template('group.py')

    context = {"sources": sources, "group": group_name}
    return template.render(context)


def generate_model(objs):
    source_files = set()
    required_objects = set()
    unique_objects = set()
    for obj in objs:
        source_files.add(obj.file_name)
        if "required-object" in obj.attributes:
            required_objects.add('"{}"'.format(obj.internal_name.lower()))

        if "unique-object" in obj.attributes:
            unique_objects.add('"{}"'.format(obj.internal_name.lower()))

    template = env.get_template('idf.py')
    context = {"generation_date": date.today(), "objs": objs, "file_names": list(source_files),
               "required_objects": ", ".join(required_objects), "unique_objects": ", ".join(unique_objects)}
    return template.render(context)


if __name__ == '__main__':
    pass