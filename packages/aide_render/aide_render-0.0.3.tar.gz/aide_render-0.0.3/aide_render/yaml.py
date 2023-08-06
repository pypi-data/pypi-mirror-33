"""aide_render's YAML decomposition logic. aide_render uses standard ruYaml with
additional tags supported. Here's a list of the currently supported tags and
their use case:
  * !q: used with a quantity string (ie: 5 meter) to represent a pint quantity.
  * !quantity: used to represent a pint quantity: <Quantity(1.25, 'liter / second')>
"""

import ruamel.yaml as standard_yaml
from ruamel.yaml.compat import StringIO
from aide_design.units import unit_registry as u
import re
from .builder_classes import DP, HP
import warnings
warnings.simplefilter('ignore', standard_yaml.error.UnsafeLoaderWarning)


# This enables us to return strings from YAML with dump_to_string
class AideRenderYAML(standard_yaml.YAML):
    def dump_to_string(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
            standard_yaml.YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


# Create the aide_render instance of YAML - this has special resolvers and constructors.
yaml = AideRenderYAML()


############################### Representers and Constructors ###########################


def builder_class_representer(dumper, data):
    # strip 'dimensionless' because there is no use for it
    representation = str(data).replace('dimensionless', '')
    return dumper.represent_scalar(tags_dict_inverted[data.__class__], representation)


def builder_class_constructor(loader, node):
    value = loader.construct_scalar(node)
    # seperate the units from the magnitude to build the quantity.
    pattern = re.compile(r'([ ]?[+-]?[0-9]*[.]?[0-9]+)')
    split_list = re.split(pattern, value)
    mag, units = split_list[1], ''.join(split_list[2:])
    return u.Quantity(float(mag), units)


############################### Turning on and off the tags ############################
# Use this section to comment out tags as necessary.

# the tags dict maps used tags to their relative classes.
tags_dict = {u'!q': u.Quantity, u'!D': DP, u'!H': HP}
tags_dict_inverted = {v: k for k, v in tags_dict.items()}

for k, v in tags_dict.items():
    yaml.representer.add_representer(v, builder_class_representer)
    yaml.constructor.add_constructor(u'!q', builder_class_constructor)

pattern = re.compile(r'[+-]?([0-9]*[.])?[0-9]+[ ]([A-z]+[/*]*[0-9]*)')
yaml.resolver.add_implicit_resolver(u'!q', pattern, None)

############################## Use to register the classes ###############################

