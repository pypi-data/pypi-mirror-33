from aide_render.yaml import yaml
from aide_design.play import *
import sys

################### YAML tag testing ###############################

# UNITS

def test_load_yaml():
    # explicit with the u tag:
    s = """ {"quantity": !q 78 m} """
    assert yaml.load(s) == {"quantity": 78*u.meter}
    # implicit:
    s = """ {"quantity": 78 m} """
    assert yaml.load(s) == {"quantity": 78 * u.meter}


def test_dump_yaml():
    # explicit with the u tag:
    s = 'quantity: 78 meter\n'
    assert yaml.dump_to_string({"quantity": 78*u.meter}) == s


def test_load_and_dump_yaml(capsys):
    s = """
explicit_q: 12 meter
implicit_q: 34 milligram / centimeter ** 3
nested:
  e: 45 milligram
  i: 10 meter ** 3"""
    loaded = yaml.load(s)
    assert loaded == {'explicit_q': 12 *u.meter, 'implicit_q': 34*u.mg/u.cm**3, 'nested': {'e': 45*u.milligram, 'i': 10*u.meter ** 3}}

def test_yaml_difficult_units():
    #a list of dictionaries to test
    d_list = []
    d_list.append({"weird": 45 * u.m**3.5/ u.pound_force_per_square_inch*u.kg})
    for d in d_list:
        yaml.dump_to_string(d)
        # check if it is dumped reliably
        assert yaml.dump_to_string(d) == yaml.dump_to_string(yaml.load(yaml.dump_to_string(d)))
        #check if d is loaded reliably
        assert yaml.load(yaml.dump_to_string(d)) == yaml.load(yaml.dump_to_string(yaml.load(yaml.dump_to_string(d))))

