import re

def insert(table, fields):
    """ Function for generating an SQL insert from a dict structure
    Args:
        table (str): The name of the table to be inserted into
        fields (dict): A dict that contains column names and the values to be inserted
    Returns:
        dictionary: returns a complete SQL string that can then be executed with parameter formatting.

        For example you can return the string and run a db execute.
        qry = PythonSQLGenerator.insert('my_table_name', my_dict)
        cursor.execute(qry['query'], qry['params'])
    """
    k = ""
    v = ()
    i = 0
    params = ""
    for key, val in fields.iteritems():
        i += 1
        k += "`" + key + "`"
        v = v + (val,)
        params += '%s'
        if i < len(fields):
            k += ", "
            params += ", "
    qry = {
        'query': "Insert Into " + table + " (%s) Values (%s);" % (k, params),
        'params': v
    }
    return qry
