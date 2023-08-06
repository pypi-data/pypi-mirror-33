import re


def delete(table, where={}):
    """ Function for generating an SQL delete from a dict structure
    Args:
        table (str): The name of the table to be deleted from
        where (dict): A dict that contains the where key and values
    Returns:
        string: returns a complete SQL string that can then be executed.

        For example you can return the string and run a db execute.
        qry = PythonSQLGenerator.delete('my_table_name', my_where_dict)
        cursor.execute(qry)
    """
    qry = ""
    # if a where clause has been passed, loop through the where dict and set the key value string
    i = 0
    for key, val in where.iteritems():
        i += 1
        qry += key + "='" + str(val) + "'"
        if i < len(where):
            qry += " and "
    qry = "delete from " + table + " where %s;" % (qry)
    return qry
