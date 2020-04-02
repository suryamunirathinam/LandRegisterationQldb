
from logging import basicConfig, getLogger, INFO

from sample_data import print_result
from connect_to_ledger import create_qldb_session

logger = getLogger(__name__)
basicConfig(level=INFO)


def scan_table(transaction_executor, table_name):
   
    logger.info('Scanning {}...'.format(table_name))
    query = 'SELECT * FROM {}'.format(table_name)
    return transaction_executor.execute_statement(query)


if __name__ == '__main__':
  
    try:
        with create_qldb_session() as session:
            # Scan all the tables and print their documents.
            tables = session.list_tables()
            for table in tables:
                cursor = session.execute_lambda(
                    lambda executor: scan_table(executor, table),
                    retry_indicator=lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
                logger.info('Scan successful!')
                print_result(cursor)
    except Exception:
        logger.exception('Unable to scan tables.')