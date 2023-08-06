def taxon_database(name, database = None):
    '''
    Make a taxon database

    :param name: [String] A database name
    :param url: [String] The database URL
    :param description: [String] A description
    :param id_regex: [String] id regex

    :return: A dict

    Usage::

        from pytaxa import constructors as cs
        cs.taxon_database("ncbi", 
            "http://www.ncbi.nlm.nih.gov/taxonomy",
            "NCBI Taxonomy Database", 
            "*")
    '''
    return {"name": name, "database": database}

def taxon_name(name, database = None):
    '''
    Make a taxon name

    :param name: [Array] A taxonomic name
    :param database: [String] A database name

    :return: A dict

    Usage::

        from pytaxa import constructors as cs
        cs.taxon_name("Poa")
        cs.taxon_name("Poa", "ncbi")
    '''
    return {"name": name, "database": database}

def taxon_rank(name, database = None):
    '''
    Make a taxon rank

    :param name: [Array] A taxonomic name
    :param database: [String] A database name

    :return: A dict

    Usage::

        from pytaxa import constructors as cs
        cs.taxon_rank("species")
        cs.taxon_rank("genus", "ncbi")
    '''
    return {"name": name, "database": database}

def taxon_id(id, database = None):
    '''
    Make a taxon id

    :param id: [Array] A taxonomic name
    :param database: [String] A database name

    :return: A dict

    Usage::

        from pytaxa import constructors as cs
        cs.taxon_id(12345)
        cs.taxon_id(12345, "ncbi")
    '''
    return {"id": id, "database": database}
