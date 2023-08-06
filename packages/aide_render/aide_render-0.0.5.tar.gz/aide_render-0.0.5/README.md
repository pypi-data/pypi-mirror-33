# aide_render

[![Build Status](https://travis-ci.org/AguaClara/aide_render.svg?branch=master)](https://travis-ci.org/AguaClara/aide_render)
[![codecov.io](https://codecov.io/github/hbetts/orbitalpy/coverage.svg?branch=master)](https://codecov.io/github/AguaClara/aide_render?branch=master)

About this project...

## Installation

Installation instructions...

## Usage

**Note: The following examples are cumulative, meaning each additional code block depends on having ran the previous blocks.** 

### Component Structure

aide_render is intended to provide an environment for building and rendering AIDE python projects. An AIDE project is a collection of Python classes that define the representation of some Fusion 360 files, as well as the files themselves. To make Fusion 360 project, use the builder classes specified in aide_render to develop a component with various design parameters. Abstractly, this would look like:

```Python
from aide_render.builder_classes import HP, DP, Component
from aide_design.units import unit_registry as u

class SpecialComponent(Component):
    # HP and DP are subclasses of u.Quantity from python.
    # This is where you specify defaults for a certain class.
    a_hydraulic_parameter = HP('5 meter')
    a_design_parameter = DP(24, u.meter)
    
    # static methods are used so that the functions don't depend on the existence of
    # these classes
    @staticmethod
    def special_add(a,b):
        return a+b
        
    
    def __init__(self, passed_in_param):
        self.output_parameter = self.special_add(passed_in_param, self.a_hydraulic_parameter)
    
``` 

Now that our component is built, we can render the design parameters that will
be used to scale the Fusion file like so:

```python
my_component = SpecialComponent(DP(30*u.meter))
from aide_render.builder import render
rendered = render(my_component)
print(rendered)
```

That will return a dictionary of ONLY THE DESIGN PARAMETERS. This means anything that was a DP class will be put into the dictionary. The rendered dict is below - notice how the HP parameter is not included:

```python
{'default_design_parameter': <Quantity(24, 'meter')>, 'output_parameter': <Quantity(35 meter, 'dimensionless')>}
```

Finally, to get the YAML that is passed to aide_draw, simply use the aide_render yaml library to dump the dict:

```python
from aide_render.yaml import dump, load
dump(rendered)
# "{a_design_parameter: !DP '24 meter', output_parameter: !DP '35 meter '}\n"
```

### Recursive Component Structure

In this example, we'll show how to subclass a component that already exists and then include another component
to be rendered within it. 

Say we have another component that is a whole lot like the Component we made, but it has one added feature. Let's
build that: 

```python
class MoreSpecialComponent(SpecialComponent):
    def __init__(self, a_special_component):
        self.special_component = a_special_component
        super(MoreSpecialComponent, self).__init__(DP('3 meter'))
```


## Contributing

Read [CONTRIBUTING](CONTRIBUTING.md).
