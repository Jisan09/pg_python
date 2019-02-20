import logging



def make_postgres_update_statement(table, kv_map, where_kv_map, clause, debug = True):
    _prefix = "UPDATE"
    clause = " " + clause + " "
    keys = ", ".join([k + "=%s" for k in list(kv_map.keys())])
    where_keys = " AND ".join([k + clause + "%s" for k in list(where_kv_map.keys())])
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = ", ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "SET", keys, "WHERE", where_keys])
    if debug:
        logging.info("Updating into Db: %s, %s" %(statement, list(kv_map.values()) + list(where_kv_map.values())))
    return statement, list(kv_map.values()) + list(where_kv_map.values())


def get_from_clause(query_values_dict_lst,columns_to_query_lst):
    """
    returns from clause that contains tuples of placeholders
    :param query_values_dict_lst:
    :param columns_to_query_lst:
    :return:
    """
    from_str = "from (values "
    length = len(columns_to_query_lst)+1
    placeholder_str = ["%s"] * length
    row_str = ",".join(placeholder_str)
    row_str = "(" + row_str + ")"
    num_of_dict = len(query_values_dict_lst)
    multi_row_str = [row_str]*num_of_dict
    multi_row_str = ",".join(multi_row_str)
    from_str = from_str +multi_row_str +")"
    return from_str


def get_as_clause(columns_to_query_lst):
    """
    get_as_clause will return all column names tuples.
    :param columns_to_query_lst: columns for where clause
    :return:
    """
    column_str = ""
    for col in columns_to_query_lst:
        column_str = column_str + col + ","
    column_str += "update"
    as_clause = "as c(" + column_str + ")"
    return  as_clause


def get_where_clause(columns_to_query_lst):
    """
    get_where_clause returns the where clause from the given query list.
    :param columns_to_query_lst: columns for where clause.
    :return:
    """
    where_str = "where "
    equals_str =[]
    for row in columns_to_query_lst:
        temp_str =  "c." + row + " = t." + row
        equals_str.append(temp_str)
    joined_str = " AND ".join(equals_str)
    where_str = where_str + joined_str
    return where_str

def get_values(column_to_query_lst, query_values_dict_lst ):
    """
    makes flat list for update values.
    :param column_to_query_lst:
    :param query_values_dict_lst:
    :return:
    """
    column_to_query_lst.append("update")
    values = []
    for dict_row in query_values_dict_lst:
        for col in column_to_query_lst:
            values.append(dict_row[col])
    return values

def make_postgres_update_multiple_statement(table,column_to_update,
                                            columns_to_query_lst,
                                            query_values_dict_lst,
                                            print_debug_log = True):
    """
    It makes query statement.
    :param table: table to update.
    :param column_to_update: column name that is to be updated.
    :param columns_to_query_lst: columns name that will we used for where clause.
    :param query_values_dict_lst: list of dictionary that contains values to update.
    :param print_debug_log:
    :return:
    """
    _prefix = "UPDATE"
    table_name = table + " as t"
    keys = column_to_update + " = c.update"
    from_clause = get_from_clause(query_values_dict_lst, columns_to_query_lst)
    as_clause = get_as_clause(columns_to_query_lst)
    where_clause = get_where_clause(columns_to_query_lst)
    statement = " ".join([_prefix, table_name, "SET", keys, from_clause, as_clause, where_clause])
    values = get_values(columns_to_query_lst, query_values_dict_lst)
    if print_debug_log == True:
       logging.info("Updating multiple rows into db %s"%(statement))
    return  statement ,values


def make_keys_multicol(columns_to_update_lst):
    """
        returns keys to be updated and new names of columns to be updated
        :param columns_to_update_lst:
        :return:
        """
    key_equal = []
    update_lst = []
    for key in columns_to_update_lst:
        temp_str = key + " = c.update" + key
        update_lst.append("update" +key)
        key_equal.append(temp_str)
    joined_str = " , ".join(key_equal)
    return joined_str, update_lst


def get_from_clause_multicol(query_values_dict_lst,columns_to_query_lst, columns_to_update_lst):
    """
        returns from clause that contains tuples of placeholders
        :param query_values_dict_lst:
        :param columns_to_update_lst:
        :param columns_to_query_lst:
        :return:
        """
    from_str = "from (values "
    length = len(columns_to_query_lst)+len(columns_to_update_lst)
    placeholder_str = ["%s"] * length
    row_str = ",".join(placeholder_str)
    row_str = "(" + row_str + ")"
    num_of_dict = len(query_values_dict_lst)
    multi_row_str = [row_str]*num_of_dict
    multi_row_str = ",".join(multi_row_str)
    from_str = from_str +multi_row_str +")"
    return from_str


def get_as_clause_multicol(columns_to_query_lst, update_param_list):
    """
        get_as_clause will return all column names tuples.
        :param columns_to_query_lst: columns for where clause
        :param update_param_list: new column names for columns to be updated
        :return:
        """
    column_str = []
    for col in columns_to_query_lst:
        column_str.append(col)
    for col in update_param_list:
        column_str.append(col)
    as_clause = ",".join(column_str)
    as_clause = "as c(" + as_clause +  ")"
    return as_clause

def get_values_multicol(column_to_query_lst, column_to_update_lst, query_values_dict_lst ):
    """
        makes flat list for update values.
        :param column_to_query_lst:
        :param query_values_dict_lst:
        :return:
        """
    values = []
    for dict_row in query_values_dict_lst:
        for col in column_to_query_lst:
            values.append(dict_row['where'][col])
        for col in column_to_update_lst:
            values.append(dict_row['update'][col])
    return values

def get_subtable_for_missing(table, columns_to_update_lst,columns_to_query_lst, query_values_dict_lst, cur):
    """
        Return subtable to fill missing values for multirow multicolumn update
        :param table: table to update into
        :param column_to_update_lst: columns to be updated clause
        :param columns_to_query_lst: column names for where clause
        :param query_values_dict_lst: values for where and Set.
        :return:
        """
    params_to_select = ",".join(columns_to_query_lst + columns_to_update_lst)
    where_clause = []
    where_values = []
    for dict_row in query_values_dict_lst:
        dict_row = dict_row['where']
        for dict_item in dict_row.items():
            where_clause.append(dict_item[0] + "=" + "%s")
            where_values.append(dict_item[1])
    where_clause = " or ".join(where_clause)
    #Make the postgresql statement
    stmt = "select " + params_to_select + " from " + table + " where " + where_clause
    try:
        cur.execute("BEGIN")
        cur.execute("lock " + table + " in access exclusive mode")
        cur.execute(stmt, where_values)
        record = cur.fetchall()
        logging.info("Selected subtable to fill missing values: %s, %s" % (stmt, where_values))
        return record
    except Exception as e:
        logging.error("Could not select subtable: ", e)
        return None

def fill_missing_values(table, columns_to_update_lst,columns_to_query_lst, query_values_dict_lst, cur):
    """
       Multiple update support in pg_python
       :param table: table to update into
       :param column_to_update: Single column for set clause
       :param columns_to_query_lst: column names for where clause
       :param query_values_dict_lst: values for where query and update params.
       :param cur: cursor object to make select and update statements.
       :return:
       """
    record = get_subtable_for_missing(table, columns_to_update_lst, columns_to_query_lst, query_values_dict_lst, cur)
    for dict_row in query_values_dict_lst:
        update_params = dict_row['update']
        where_params = dict_row['where']
        len_where_params = len(where_params)
        if len(update_params)==len(columns_to_update_lst):  #All update columns present, so pass
            pass
        else:
            recs_to_ins = []
            for rec in record:
                result = list(rec[0:len_where_params])==list(where_params.values())
                if result:
                    recs_to_ins.extend(rec[len_where_params:])
                    break

            if len(recs_to_ins)>0:
                for col in columns_to_update_lst:
                    if col not in update_params:
                        update_params[col] = recs_to_ins[columns_to_update_lst.index(col)]
            else:
                for col in columns_to_update_lst:
                    if col not in update_params:
                        update_params[col] = None
    print(query_values_dict_lst)
    return query_values_dict_lst

def check_parameters_multicol(columns_to_update_lst, columns_to_query_lst, query_values_dict_lst):
    """
           check_prarameters checks whether the passed parameters are valid or not.
           :param column_to_update: name of column that is to be updated.
           :param columns_to_query_lst: list of column names that is used in where clause.
           :param query_values_dict_lst: list of dictionaries containing values for where clause and target column.
           :return: boolean
           """
    expected_length_query_cols = len(columns_to_query_lst)
    expected_length_target_cols = len(columns_to_update_lst)
    for dict_val in query_values_dict_lst:
        #Check length of query columns
        if len(dict_val['where'])!=expected_length_query_cols:
            logging.error("%s doesn't match the dimensions" % (dict_val))
            return False
        #Check length of target columns
        if len(dict_val['update'])>expected_length_target_cols:
            logging.error("%s doesn't match the dimensions" % (dict_val))
            return False
        # check columns present in update params
        for key in dict_val['update']:
            if key not in columns_to_update_lst:
                logging.error("%s attribute to update isn't present in update list" % (key))
                return False
        # check columns present in query where params
        for key in dict_val['where']:
            if key not in columns_to_query_lst:
                logging.error("%s attribute to update isn't present in query list" % (key))
                return False
    return True

def make_postgres_update_multiple_column_statement(table, columns_to_update_lst, columns_to_query_lst,
                                                   query_values_dict_lst, print_debug_log = True):
    """
    It makes query statement.
    :param table: table to update.
    :param column_to_update_lst: column names  to be updated.
    :param columns_to_query_lst: columns name that will we used for where clause.
    :param query_values_dict_lst: list of dictionary that contains values to update and where clause values.
    :param print_debug_log:
    :return:
    """
    _prefix = "UPDATE"
    table_name = table + " as t"
    keys, update_param_list = make_keys_multicol(columns_to_update_lst)
    from_clause = get_from_clause_multicol(query_values_dict_lst, columns_to_query_lst, columns_to_update_lst)
    as_clause = get_as_clause_multicol(columns_to_query_lst, update_param_list)
    where_clause = get_where_clause(columns_to_query_lst)
    statement = " ".join([_prefix, table_name, "SET", keys, from_clause, as_clause, where_clause])
    values = get_values_multicol(columns_to_query_lst, columns_to_update_lst, query_values_dict_lst)
    if print_debug_log == True:
        logging.info("Updating multiple rows into db %s, %s" % (statement, values))
    return statement, values