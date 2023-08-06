Rigo Core

DBEngine:

1. list-databases, list-tables, search-database, search-global, search-table
   > range-search, item-search (list)

2. Optional grouped views (uniform_dataset)

3. (inner) join by list comprehension

t1 = [{"a":"apple"},{"b":"bee"},{"c":"cat"}]
t2 = [{"a":"artist"},{"b":"ball"},{"c":"cat"}]
t3 = [{"a":"apple"},{"b":"bat"},{"c":"coriander"}]

join t1,t2,t3 where "a" = "apple"

[row for row in t1 if "a" in row]

[row for row in [row for row in t1 if "a" in row] if row["a"]=="apple"]
[row for row in [row for row in t2 if "a" in row] if row["a"]=="apple"]
[row for row in [row for row in t3 if "a" in row] if row["a"]=="apple"]

def safely_evaluate(options):
    safe_copy = {}
    for key in options:
        safe_copy[str(key).lower()] = options[key]
    return safe_copy, safe_copy.keys()


def join(table_list,join_field,join_values,ranged=False,grouped=False):

    def predicate():
        if ranged:
            return "range"
        else:
            return "item"

    def meetsCondition(subject,object,predicate):
        if predicate == "item":
            return subject in object
        elif predicate == "range":
            min_ = min(object)
            max_ = max(object)
            return bool(subject>=min_ and subject<=max_)
        else:
            return False

    joined_table = []
    for table in table_list:
        try:
            dbname,tablename = table.split('.')
            table_data = ReadDBCache()[dbname].Tables[tablename];
            for row in [row for row in [row for row in table_data if join_field in row] if meetsCondition(row[join_field],join_values,predicate())]:
                joined_table.append(row)
        except:
            pass
    if grouped:
        return uniform_dataset(joined_table)
    else:
        return joined_table
