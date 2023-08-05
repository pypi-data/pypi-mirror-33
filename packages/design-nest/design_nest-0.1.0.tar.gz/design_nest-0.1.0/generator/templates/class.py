class {{obj.class_name}}(BaseObject):
    """ Corresponds to object `{{ obj.eplus_name }}` """
    _schema = {{obj.schema}}

    {%- for field in obj.fields %}

    @property
    def {{field}}(self):
        return self["{{ field }}"]

    @{{field}}.setter
    def {{field}}(self, value=None):
        self["{{ field }}"] = value
    {%- endfor %}
        