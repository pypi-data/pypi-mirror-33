from aide_design.units import unit_registry as u

def assert_types(variables: dict, types_dict: dict, strict=True, silent=False):
    """Check variables against their expected type. Also can check more complex types, such as whether the expected
    and actual dimensionality of pint units are equivalent.
    Parameters
    ----------
    variables : dict
        Contain variable_name : variable_object key-value pairs.
    types_dict : dict
        A dictionary containing variable:type key value pairs.
    strict :obj: bool, optional
        If true, the function ensures all the variables in types_dict are present in variables.
    silent :obj: bool, optional
        If true, the function only returns a boolean rather than throwing an error.
    Returns
    -------
    bool
        True if the variables dict passes the assert_inputs check as described.
    Raises
    ------
    ValueError
        If silent is turned to false and the inputs do not pass the assert_inputs test
    Examples
    --------
    Standard usage showing a passing collection of parameters. This passes both the non-strict and strict options.
    >>> variables = {"a" : 1, "b" : 1.0, "c" : "string"}
    >>> types_dict = {"a" : int, "b" : float, "c" : str}
    >>> assert_types(variables,types_dict)
    True

    Wrong types error thrown:
    >>> types_dict = {"a" : str, "b" : str, "c" : str}
    >>> assert_types(variables,types_dict)
    Traceback (most recent call last):
    TypeError: Can't convert the following implicitly: {'a': "Actual type: <class 'int'> Intended type: <class 'str'>", 'b': "Actual type: <class 'float'> Intended type: <class 'str'>"}.

    Not enough variables are present:
    >>> assert_types({"a":1}, {"a":int, "b": int})
    Traceback (most recent call last):
    NameError: names 'b' are not defined

    Use with units:
    >>> from aide_design.play import *
    >>> assert_types({"length" : 1*u.meter},{"length" : u.mile})
    True
    >>> assert_types({"length" : 1*u.meter**2},{"length" : u.mile})
    Traceback (most recent call last):
    TypeError: Can't convert the following implicitly: {'length': 'Actual dimensionality: [length] ** 2 Intended dimensionality: [length]'}.
    """
    # Store the intended types
    type_error_dicionary = {}
    # Store the missing variables
    missing = []

    for name, t in types_dict.items():
        try:
            var = variables[name]

            #check for recursive dicts. If there are, then recurse.
            if isinstance(t, dict):
                assert_types(var, t)

            # check if this is a pint variable and has compatible dimensionality.
            if isinstance(var, u.Quantity):
                if not var.dimensionality == t.dimensionality:
                    type_error_dicionary[name] = "Actual dimensionality: {} Intended dimensionality: {}".format(
                        var.dimensionality, t.dimensionality)

            # check if types are compatible
            elif not isinstance(var, t):
                type_error_dicionary[name] = "Actual type: {} Intended type: {}".format(type(var), t)

        # If the variable is missing
        except KeyError:
            missing.append(name)

    check = not type_error_dicionary
    if strict and check:
        check = not missing

    if not silent and not check:
        if missing:
            raise NameError("names {} are not defined".format("'" + "', '".join(missing) + "'"))
        if type_error_dicionary:
            raise TypeError("Can't convert the following implicitly: {}.".format(type_error_dicionary))
    return check