# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# This code expects that you have AWS credentials setup per:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
from datetime import datetime, timedelta
from logging import basicConfig, getLogger, INFO

from sample_data import print_result, get_document_ids, SampleData
from constants import Constants
from connect_to_ledger import create_qldb_session

logger = getLogger(__name__)
basicConfig(level=INFO)


def format_date_time(date_time):
    
    return date_time.strftime('`%Y-%m-%dT%H:%M:%S.%fZ`')


def previous_owners(transaction_executor, surveyno):
 
    # person_ids = get_document_ids(transaction_executor, Constants.LAND_REGISTRATION_TABLE_NAME, 'SurveyNO', surveyno)

    # todays_date = datetime.utcnow() - timedelta(seconds=1)
    # three_months_ago = todays_date - timedelta(days=90)
    # query = 'SELECT data.Owners, metadata.version FROM history({}, {}, {}) AS h WHERE h.metadata.id = ?'.\
    #     format(Constants.LAND_REGISTRATION_TABLE_NAME, format_date_time(three_months_ago),
    #            format_date_time(todays_date))
    query= "select h.metadata,q.data.FirstName,q.data.LastName from history(LandRegistration) as h inner join _ql_committed_Person as q on h.data.Owners.PersonId=q.metadata.id where h.data.SurveyNO='{}'".format(surveyno)
    
    logger.info("Querying the 'LandRegistration' table's history using surveyno: {}.".format(surveyno))
    cursor = transaction_executor.execute_statement(query)
    return cursor
        


if __name__ == '__main__':
    
    try:
        with create_qldb_session() as session:
            surveyno = SampleData.LAND_REGISTRATION[0]['SurveyNO']
            session.execute_lambda(lambda lambda_executor: previous_owners(lambda_executor,surveyno),
                                   lambda retry_attempt: logger.info('Retrying due to OCC conflict...'))
            logger.info('Successfully queried history.')
    except Exception:
        logger.exception('Unable to query history to find previous owners.')