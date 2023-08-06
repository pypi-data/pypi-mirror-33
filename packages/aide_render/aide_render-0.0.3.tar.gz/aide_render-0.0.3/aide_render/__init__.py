"""Main aide_render designs. All designs should go in here. For now, the syntax for building a design is:
aide_render(yaml_string)
The root of the YAML string is the name of a class that will be built to represent that string. Any inner parameters
are passed directly to the init functioin of that class. The return is an output YAML of the finished design.
"""

import sys

def render_lfom(yaml_path: str, stream_out=sys.stdout, yaml_path_out=None):
    """

    Parameters
    ----------
    yaml_path
        This is the path to the place that defines the LFOM.
    stream_out:opt: sys.stdout
        This is which stream to write the output to. Defaults to the standard out.
    yaml_path_out:opt:None
        This is where to write the output (which file path.)

    Returns
    -------
    Fully defined design YAML for an LFOM. The YAML that is
    taken in looks like:

    q: 45

    Units are interpreted based on the name. q is in L/s

    Examples
    --------
    >>> import aide_render
    >>> import os
    >>> file_path = os.path.join(os.path.dirname(__file__), "./example_yaml_params/lfom_inputs.yaml")
    >>> aide_render.render_lfom(file_path, yaml_path_out="test.yaml")
    CommentedMap([('q', 70)])
    params:
      ratio_safety: 1.5
      sdr: 26
      hl: 20 centimeter
      q: 70 liter / second
    dp:
      b_row: 5 centimeter
      od: 18 inch
      d_orifice: 0.03125 meter
      n_row1: 44
      n_row3: 0
      n_row5: 0
      n_row7: 0
      n_row9: 19
      n_row11: 0
      n_row13: 0
      n_row15: 0
      n_row17: 16
      n_row19: 0
      n_row21: 0
      n_row23: 0
      n_row25: 12
      n_row27: 0
      n_row29: 0
      n_row31: 0

    """
    from aide_render.yaml import yaml
    from aide_render.builder_classes import DP, HP
    from .templates.lfom import LFOM
    from aide_design.units import unit_registry as u
    import sys
    from aide_render.builder import extract_types
    from types import SimpleNamespace

    with open(yaml_path, 'r') as f:
     user_params = yaml.load(f)

    print(user_params)

    name_unit_mapping = {"q": u.L/u.s}

    kwargs = {}

    try:
        for name, value in user_params.items():
            try:
                kwargs[name] = value*name_unit_mapping[name]
            except:
                UserWarning("{} isn't in the name_unit_mapping dictionary and thus has unspecified units.".format(name))
    except:
        raise UserWarning("Yaml loaded from {} needs to map to dictionary, not a {}: {}".format(yaml_path, type(user_params), user_params))

    my_lfom = LFOM(**kwargs)
    lfom_design_dict = extract_types(my_lfom, [u.Quantity, int, float], [SimpleNamespace])
    yaml.dump(lfom_design_dict, stream=sys.stdout)

    if stream_out:
        yaml.dump(lfom_design_dict, stream=stream_out)
    if yaml_path_out:
        with open(yaml_path_out, 'w+') as f:
            yaml.dump(lfom_design_dict, stream=f)