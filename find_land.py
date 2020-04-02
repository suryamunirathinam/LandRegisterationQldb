
from logging import basicConfig, getLogger, INFO

from sample_data import get_document_ids, print_result, SampleData
from constants import Constants
from connect_to_ledger import create_qldb_session

logger = getLogger(__name__)
basicConfig(level=INFO)


def find_lands_for_owner(transaction_executor, gov_id):
  
    document_ids = get_document_ids(transaction_executor, Constants.PERSON_TABLE_NAME, 'GovId', gov_id)

    query = "SELECT Land FROM Land INNER JOIN LandRegistration AS r " \
            "ON Land.SurveyNO = r.SurveyNO WHERE r.Owners.PersonId = ?"

    for ids in document_ids:
        cursor = transaction_executor.execute_statement(query, ids)
        logger.info('List of Lands for owner with GovId: {}...'.format(gov_id))
        print_result(cursor)


if __name__ == '__main__':
    """
    Find all Lands registered under a person.
    """
    try:
        with create_qldb_session() as session:
            # Find all lands registered under a person.
                gov_id = SampleData.PERSON[0]['GovId']
                # for each in SampleData.PERSON:
                # gov_id = each['GovId']
                session.execute_lambda(lambda executor: find_lands_for_owner(executor, gov_id),
                                    lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
    except Exception:
        logger.exception('Error getting lands for owner.')