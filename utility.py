import inspect
def self_string() -> str:
    """
    Returns the contents of the current file as a string
    """
    with open(inspect.stack()[1].filename, 'r') as f:
        s = f.read()
    return s