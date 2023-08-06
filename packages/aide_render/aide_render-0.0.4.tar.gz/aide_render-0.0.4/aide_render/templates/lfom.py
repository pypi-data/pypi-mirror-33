import aide_design.materials_database as mat
import aide_design.pipedatabase as pipe
import numpy as np
from aide_design.units import unit_registry as u
from aide_render.yaml import yaml
from types import SimpleNamespace
from ..utilities import assert_types


class LFOM:
    r""" This is an example class for an LFOM. It already has a lot of features built in,
    such as defaults that go in the class attribute section, and methods associated with the class.
    As well as an instantiation process that can be used to set custom values. In general, a class
    gets inputs passed in through the init function in the form of keyword args. The keyword args
    that are required are specified within the docstring. Furthermore, arguments can be type checked
    using the assert_types function in the utilities module. When the LFOM class is created, the final
    class is meant to represent an LFOM that can then be designed by CAD. Therefore, all CAD output
    parameters are placed into the special "dp" instance field.

    Attributes
    ----------
    These are the default values for an LFOM. To overwrite, pass these in as keywords.

    ratio_safety : float
        Percent above the top hole safety height.
    sdr : float
        Standard dimensional ratio of the LFOM pipe.
    b_orifice : length
        Minimum distance between orifices.
    hl : length
        Headloss of the LFOM



    Methods
    -------
    All these methods are just imported from the aide_design lfom.

    n_lfom_rows(q, hl_lfom)
        number of rows of orifices in an lfom. This could be defined directly
        within the LFOM class here instead of in lfom_prefab... just copy & paste!
    nom_diam_lfom_pipe(q, hl_lfom)
        nominal diameter of the lfom pipe.
    orifice_diameter(q, hl_lfom, mat.DIAM_DRILL_ENG)
        orifice diameter
    n_lfom_orifices_fusion
        List of numbers of rows

    Examples
    --------

    >>> my_lfom = LFOM(q=30*u.L/u.s)
    >>> import sys
    >>> from aide_render.builder import extract_types
    >>> lfom_design_dict = extract_types(my_lfom, [u.Quantity, int, float], [SimpleNamespace])
    >>> #print(lfom_design_dict)
    >>> from aide_render.yaml import yaml
    >>> yaml.dump(lfom_design_dict, stream=sys.stdout)
    params:
      ratio_safety: 1.5
      sdr: 26
      hl: 20 centimeter
      q: 30 liter / second
    dp:
      b_row: 5 centimeter
      od: 12.75 inch
      d_orifice: 0.03125 meter
      n_row_1: 19
      n_row_2: 0
      n_row_3: 0
      n_row_4: 0
      n_row_5: 8
      n_row_6: 0
      n_row_7: 0
      n_row_8: 0
      n_row_9: 7
      n_row_10: 0
      n_row_11: 0
      n_row_12: 0
      n_row_13: 5
      n_row_14: 0
      n_row_15: 0
      n_row_16: 0

    """

    ############## ATTRIBUTES ################
    # Set the default input for the class
    params = SimpleNamespace(ratio_safety=1.5,
                             sdr=26,
                             hl=20*u.cm
                             )



    ############### METHODS #################
    # Methods I import that are already defined in the functional layer.
    from aide_design.unit_process_design.lfom import (
        n_lfom_rows,
        nom_diam_lfom_pipe,
        orifice_diameter,
        n_lfom_orifices,
    )
    # We have to turn these into static methods so that the instance isn't passed in!
    n_lfom_rows = staticmethod(n_lfom_rows)
    nom_diam_lfom_pipe = staticmethod(nom_diam_lfom_pipe)
    orifice_diameter = staticmethod(orifice_diameter)
    n_lfom_orifices = staticmethod(n_lfom_orifices)


    # This function takes the output of n_lfom_orifices and converts it to a list with 16
    # entries that corresponds to the 16 possible rows. This is necessary to make the lfom
    # easier to construct in Fusion using patterns
    @staticmethod
    @u.wraps(None, [u.m ** 3 / u.s, u.m, u.inch, None], False)
    def n_lfom_orifices_fusion(FLOW, HL_LFOM, drill_bits, num_rows):
        num_orifices_per_row = LFOM.n_lfom_orifices(FLOW, HL_LFOM, drill_bits) #array of number of orifices on each row.
        num_orifices_fianl_per_row = np.zeros(16) # output array
        n_rows_in = num_orifices_per_row.size
        for i in range(n_rows_in):
            num_orifices_fianl_per_row[int(i * 16/n_rows_in)]=num_orifices_per_row[i]

        return num_orifices_fianl_per_row


    def __init__(self, **kwargs):
        """
        This is where the "instantiation" occurs. Think of this as "rendering the
        template" or "using the cookie-cutter to make the cookie". Here is where we
        call all the methods that determine design parameters of the specific LFOM
        we are building.

        Parameters
        ----------
        q : flow rate
            The max flow rate the LFOM can handle
        """

        # Check the types of the required inputs
        required = {"q": u.L/u.s}
        assert_types(kwargs, required)


        # Check the types of the optional inputs
        optional = {"hL": u.cm}
        assert_types(kwargs, optional, strict=False)

        # Where the output sent to Fusion is stored
        self.dp = SimpleNamespace()
        dp = self.dp

        params = self.params

        # add kwargs as instance fields to params
        for k, v in kwargs.items():
            setattr(params, k, v)

        n_rows = self.n_lfom_rows(params.q, params.hl)
        dp.b_row = params.hl/n_rows
        dp.od = pipe.OD(self.nom_diam_lfom_pipe(params.q, params.hl))
        dp.d_orifice = self.orifice_diameter(params.q, params.hl, mat.DIAM_DRILL_ENG)
        num_orifices_final = self.n_lfom_orifices_fusion(params.q, params.hl, mat.DIAM_DRILL_ENG, n_rows)
        i=0
        for num_per_row in num_orifices_final:
            setattr(dp, 'n_row_' + str(i+1), int(num_per_row))
            i += 1

yaml.register_class(LFOM)

import ruamel.yaml.error