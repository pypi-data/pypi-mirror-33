import logging


def make_postgres_delete_statement(table, kv_map, debug):
    _prefix = "DELETE FROM "
    keys = " and ".join([k + "=%s" for k in kv_map.keys()])
    statement = " ".join([_prefix, table, " where ", keys])
    if debug:
        logging.info("Deleting from Db: %s, %s" % (statement, kv_map.values()))
    return statement, list(kv_map.values())
