
from logging import basicConfig, getLogger, INFO

from sample_data import get_document_ids, print_result, SampleData
from constants import Constants
from sample_data import convert_object_to_ion
from connect_to_ledger import create_qldb_session

logger = getLogger(__name__)
basicConfig(level=INFO)


def find_person_from_document_id(transaction_executor, document_id):
    
    query = 'SELECT p.* FROM Person AS p BY pid WHERE pid = ?'
    cursor = transaction_executor.execute_statement(query, document_id)
    return next(cursor)


def find_owner_for_land(transaction_executor, surveyno):
    
    logger.info('Finding owner for land with surveyno: {}.'.format(surveyno))
    query ="SELECT r.Owners ,q.data.FirstName,q.data.LastName FROM LandRegistration AS r inner join _ql_committed_Person as q on r.Owners.PersonId=q.metadata.id WHERE r.SurveyNO='{}'".format(surveyno) 
    cursor = transaction_executor.execute_statement(query)
    
    try:
        return cursor
    except StopIteration:
        logger.error('No primary owner registered for this land .')
        return None
    
def find_person_land_bygovid(transaction_executor,govid):
    logger.info('Finding land info with owner for land with GovId: {}.'.format(govid))
    query="SELECT l.*,q.data.FirstName,q.data.LastName from LandRegistration as l inner join _ql_committed_Person as q on l.Owners.PersonId=q.metadata.id where q.data.GovId = '{}'".format(govid)
    cursor = transaction_executor.execute_statement(query)
    print(cursor)
    print(query)
    try:
        return cursor
    except StopIteration:
        logger.error('No primary owner registered for this land .')
        return None


def update_land_registration(transaction_executor, surveyno, document_id):
   
    logger.info('Updating the primary owner for land with SurveyNO: {}...'.format(surveyno))
    statement = "UPDATE LandRegistration AS r SET r.Owners.PersonId = ? WHERE r.SurveyNO= ?"
    cursor = transaction_executor.execute_statement(statement, document_id, convert_object_to_ion(surveyno))
    try:
        print_result(cursor)
        logger.info('Successfully transferred land with surveyno: {} to new owner.'.format(surveyno))
    except StopIteration:
        raise RuntimeError('Unable to transfer vehicle, could not find registration.')


def validate_and_update_registration(transaction_executor, surveyno, current_owner, new_owner):
   
    primary_owner = find_owner_for_land(transaction_executor, surveyno)
    if primary_owner is None or primary_owner['GovId'] != current_owner:
        raise RuntimeError('Incorrect primary owner identified for Land, unable to transfer.')

    document_id = next(get_document_ids(transaction_executor, Constants.PERSON_TABLE_NAME, 'GovId', new_owner))

    update_land_registration(transaction_executor, surveyno, document_id)


if __name__ == '__main__':
  
    land_surveyno = SampleData.LAND[0]['SurveyNO']
    previous_owner = SampleData.PERSON[0]['GovId']
    new_owner = SampleData.PERSON[1]['GovId']

    try:
        with create_qldb_session() as session:
            session.execute_lambda(lambda executor: validate_and_update_registration(executor, land_surveyno,
                                                                                     previous_owner, new_owner),
                                   retry_indicator=lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
    except Exception:
        logger.exception('Error updating VehicleRegistration.')