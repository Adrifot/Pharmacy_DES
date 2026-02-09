def read_file(filename):
    """Read the contents of a file.
    
    Parameters
    ----------
    filename: str
        Path to file.
    
    Returns
    -------
    str
        Contents of the file.
    """
    with open(filename) as f:
        return f.read() 
    