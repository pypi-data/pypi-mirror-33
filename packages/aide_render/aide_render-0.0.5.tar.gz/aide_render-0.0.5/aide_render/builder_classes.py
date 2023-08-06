"""All tier 1 classes used to build design components"""

from aide_design.units import unit_registry as u


class Q(u.Quantity):
    """A Q (quantity) is an AIDE quantity.
    """
    ...


class DP(Q):
    """A Design Parameter is a pint quantity that is passed into Fusion to draw the plant. Classes that have design
    parameters as properties are considered Fusion component classes, and should have a corresponding Fusion component.

    Examples
    --------

    """
    ...


class HP(Q):
    """A Hydraulic Parameter is a pint quantity used to characterize the hydraulic properties of a certain plant process.
    """
    ...


def make_dp_fields(init_function):
    """Turn all DP keywords into instance fields with the same names. This is syntactic sugar that reduces the unnecessary
    instance field assignments.

    This is a wrapper, so put it directly over the init function of your component.

    Examples
    --------
    # >>> from aide_design.units import unit_registry as u
    >>> class Block:
    ...     def poo(self):
    ...         return "poo"
    ...     @make_dp_fields
    ...     def __init__(self, L=DP(4,u.m), h=DP(2,u.m), w=DP(20,u.m)):
    ...         ...
    >>> my_standard_block = Block()
    >>> print(my_standard_block)
    <aide_render.builder_classes.Block object at ...

    # >>> my_standard_block.h
    TODO: finish this function
    """
    def wrapped_function(self, *args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, DP):
                setattr(self, k, v)
        return init_function(self, *args, **kwargs)
    return wrapped_function


class Component(object):
    """A component that can be drawn in CAD."""
    ...
