"""A module that can build instances of plant components into a valide aide_draw yaml"""
from aide_render.builder_classes import DP, Component
from .yaml import yaml
from time import strftime
import os

def extract_types(instance: object, collect_types: list, recurse_types: list) -> dict:
    """Take in an instance of a class and recursively extract all specified types from the class's attributes to
    construct a dict.

    Parameters
    ----------
    instance
        The instance that will be filtered.
    collect_types
        The instance types
    recurse_types
        The instance types on which to recurse.



    """
    d_prime = {}

    class_dict = dict(vars(instance.__class__))
    try:
        instance_dict = dict(vars(instance))
    except TypeError:
        instance_dict = instance

    d = {}

    if class_dict:
        d.update(class_dict)
    if instance_dict:
        d.update(instance_dict)

    if d:
        for name, var in d.items():
            for t in collect_types:
                if isinstance(var, t):
                    d_prime[name] = var
                    break
            for t in recurse_types:
                if isinstance(var, t):
                    d_prime[name] = extract_types(var, collect_types, recurse_types)
                    break
    return d_prime