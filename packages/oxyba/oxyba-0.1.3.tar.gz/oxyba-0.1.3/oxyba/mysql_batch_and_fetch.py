
def mysql_batch_and_fetch(mysql_config, *sql_queries):
    """
    Excute a series of SQL statements before the final Select query

    Parameters
    ---------- 
    mysql_config : dict
        The user credentials as defined in MySQLdb.connect, e.g. 
        mysql_conig = {'user': 'myname', 'passwd': 'supersecret', 'host': '<ip adress or domain>', 'db': '<myschema>'}

    sql_queries : list or tuple
        A list or tuple of SQL queries wheras the last SQL command
        have to be final Select query. 
        (If a string is provided the semicolon ";" is used to split
         the string into a list of strings)

    Returns
    -------
    result_table : tuple
        The result table as tuple of tuples.

    Sources
    -------
    * http://mysqlclient.readthedocs.io/user_guide.html
    """
    #load modules
    import MySQLdb as mydb
    import sys, gc

    #ensure that `sqlqueries` is a list/tuple
    #split a string into a list
    if len(sql_queries) == 1:
        if isinstance(sql_queries[0], str):
            sql_queries = sql_queries[0].split(";")
        if isinstance(sql_queries[0], (list,tuple)):
            sql_queries = sql_queries[0]

    #connect and execute queries
    try:
        conn = mydb.connect(**mysql_config)
        curs = conn.cursor()
        for sql_query in sql_queries:
            if len(sql_query)>0:
                curs.execute(sql_query)
        result_table = curs.fetchall()
    except mydb.Error as err:
        print(err); 
        gc.collect(); 
        sys.exit(1)
    else: 
        if conn: conn.close()
        gc.collect()
        return result_table