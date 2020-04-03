from django.shortcuts import render
from pyqldb.driver.pooled_qldb_driver import PooledQldbDriver
import connect_to_ledger
import insert_document
from constants import Constants
from datetime import datetime
import json
import sample_data
import modify_documents
import revision_history
from amazon.ion.simpleion import dumps, loads
# Create your views here.
def index(request):
    try:
        qldb_session = connect_to_ledger.create_qldb_session()
        connect_to_ledger.logger.info('Listing table names ')
        for table in qldb_session.list_tables():
            connect_to_ledger.logger.info(table)
        
    except ClientError:
        connect_to_ledger.logger.exception('Unable to create session.')
    
    if request.method == 'POST':
        if 'post_person' in request.POST:
            firstname=request.POST.get('firstname')
            lastname=request.POST.get('lastname')
            address=request.POST.get('address')
            dob=request.POST.get('dob')
            govid=request.POST.get('govid')
            govidtype=request.POST.get('govidtype')

            data={
            'FirstName': firstname,
            'LastName': lastname,
            'Address': address,
            'DOB':datetime.strptime(dob,'%Y-%m-%d'),
            'GovId': govid,
            'GovIdType': govidtype
            }
                              
            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    session.execute_lambda(lambda executor: insert_document.insert_documents(executor,Constants.PERSON_TABLE_NAME,data),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('Documents inserted successfully!')
            except Exception:
                connect_to_ledger.logger.exception('Error inserting or updating documents.')
            return render(request,'index.html',{'message':'Person information inserted successfully'})
        elif 'post_land' in request.POST:
            surveyno=request.POST.get('surveyno')
            landtype=request.POST.get('landtype')
            sqfeet=request.POST.get('sqfeet')
            
            data={
            'surveyno': surveyno,
            'landtype': landtype,
            'sqfeet': sqfeet
            
            }
                              
            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    session.execute_lambda(lambda executor: insert_document.insert_documents(executor,Constants.LAND_TABLE_NAME,data),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('Documents inserted successfully!')
            except Exception:
                connect_to_ledger.logger.exception('Error inserting or updating documents.')


            return render(request,'index.html',{'message':'Land information inserted successfully'})
        
        elif 'get_personid' in request.POST:
            get_govid = request.POST.get('get_govid')
            print(get_govid)
            try:
                with connect_to_ledger.create_qldb_session() as session:

                    personid = session.execute_lambda(lambda executor:sample_data.get_document_ids(executor,get_govid),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('id retrived successfully ')
                    
            except Exception:
                connect_to_ledger.logger.exception('error retriving id')
                personid = 'Gov Id incorrect'
            return render(request,'index.html',{'person_id':personid})

        elif 'get_currentowner' in request.POST:
            post_surveyno = request.POST.get('post_surveyno')
            
            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    surveyno = session.execute_lambda(lambda executor:modify_documents.find_owner_for_land(executor,post_surveyno),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('owner  retrived successfully ')
                    
                    print(surveyno)
                    ownerdata = list(map(lambda table:[table.get('FirstName'),table.get('LastName'),table.get('Owners')['PersonId']], surveyno))[0]
                   
                    print(ownerdata)
                    
            except Exception:
                connect_to_ledger.logger.exception('error retriving owner')
                ownerdata= 'Survey no incorrect'
            return render(request,'index.html',{'ownerdata':ownerdata})

        elif 'get_personland' in request.POST:
            person_govid = request.POST.get('person_govid')
            print(person_govid)
            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    personland_data= session.execute_lambda(lambda executor:modify_documents.find_person_land_bygovid(executor,person_govid),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('personlanddata retrived successfully ')
                    print(personland_data)
                    personland_data = list(map(lambda table: [table.get('FirstName'),table.get('LastName'),
                    table.get('Owners')['PersonId'],table.get('SurveyNO'),
                    table.get('LandRegNo'),table.get('State'),table.get('City'),str(table.get('MarketValue'))],personland_data))
                    print(personland_data)
            except Exception:
                connect_to_ledger.logger.exception('error retriving id')
                personland_data= 'Gov Id incorrect'
            return render(request,'index.html',{'personland_data':personland_data})

        # land Registration :
        elif 'post_landreg' in request.POST:
            surveyno=request.POST.get('reg_surveyno')
            landregno=request.POST.get('reg_landno')
            state=request.POST.get('reg_state')
            city=request.POST.get('reg_city')
            marketvalue=request.POST.get('reg_value')
            personid=request.POST.get('reg_personid')

            data={
            'SurveyNO': surveyno,
            'LandRegNo': landregno,
            'State': state,
            'City':city,
            'MarketValue': marketvalue,
            'Owners': {
                'PersonId': personid}
            }

            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    session.execute_lambda(lambda executor: insert_document.insert_documents(executor,Constants.LAND_REGISTRATION_TABLE_NAME,data),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('Land Registration is successfull ')
            except Exception:
                connect_to_ledger.logger.exception('Error Registering land')
            return render(request,'index.html',{'Reg_Status':'Land Registration details inserted successfully'})


        elif 'post_updland' in request.POST:
            surveyno=request.POST.get('upd_surveyno')
            
            personid=request.POST.get('upd_personid')

            try:
                with connect_to_ledger.create_qldb_session() as session:
        
                    upd_personland= session.execute_lambda(lambda executor:modify_documents.update_land_registration(executor,surveyno,personid),
                                        lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('Updated land info successfully ')
                    upd_personland="updated land info"
            except Exception:
                connect_to_ledger.logger.exception('error in updation ')
                upd_personland= 'Gov Id incorrect'
            return render(request,'index.html',{'upd_personland':upd_personland})
        
        elif 'post_rev' in request.POST:
            surveyno =request.POST.get('rev_surveyno')
            print(surveyno)
            try:
                with connect_to_ledger.create_qldb_session() as session:
                    result_data=session.execute_lambda(lambda executor:revision_history.previous_owners(executor,surveyno),
                                   lambda retry_attempt: connect_to_ledger.logger.info('Retrying due to OCC conflict...'))
                    connect_to_ledger.logger.info('Successfully queried history.')
                    
                    result= list(map(lambda table:[table.get('FirstName'),table.get('LastName'),table.get('metadata')],result_data))
                    
                    print (result)
                        
                    # for data in result_data:
                    #     result= list(map(lambda table:[table.get('FirstName'),table.get('LastName')],data))
                    #     print(result)
            except Exception:
                connect_to_ledger.logger.exception('Unable to query history to find previous owners.')
            return render(request,'index.html',{'result':result})
    else:
        return render(request,'index.html')


    

 
    


