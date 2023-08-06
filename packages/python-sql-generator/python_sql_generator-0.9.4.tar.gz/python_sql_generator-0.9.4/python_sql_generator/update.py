import re


def update(table, fields, where={}):
    """ Function for generating an SQL update from a dict structure
    Args:
        table (str): The name of the table to be updated
        fields (dict): A dict that contains column names and the values to be inserted
        where (dict): A dict that contains the where key and values
    Returns:
        string: returns a complete SQL string that can then be executed.

        For example you can return the string and run a db execute.
        qry = PythonSQLGenerator.update('my_table_name', my_dict, my_where_dict)
        cursor.execute(qry)
    """
    qry = ""
    i = 0
    v = ()
    params = ""
    #  loop through fields and set key and value string
    for key, val in fields.iteritems():
        i += 1
        qry += "`" + key + "`=%s"
        v = v + (val,)
        if i < len(fields):
            qry += ", "
    # if a where clause has been passed, loop through the where dict and set the key value string
    if len(where) > 0:
        i = 0
        qry += " where "
        for key, val in where.iteritems():
            i += 1
            qry += key + "=%s"
            v = v + (val,)
            if i < len(where):
                qry += " and "
    qry = {
        'query': "update " + table + " set %s;" % (qry),
        'params': v
    }
    return qry