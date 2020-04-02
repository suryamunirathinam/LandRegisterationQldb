from django.shortcuts import render
from pyqldb.driver.pooled_qldb_driver import PooledQldbDriver
import connect_to_ledger
import insert_document
from constants import Constants
from datetime import datetime
import sample_data
import modify_documents
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
                    
                
                    ownerdata = list(map(lambda table: [table.get('FirstName'),table.get('LastName'),table.get('Owners')['PersonId']], surveyno))[0]
                   
                    print(ownerdata)
                    
            except Exception:
                connect_to_ledger.logger.exception('error retriving owner')
                surveyno= 'Survey no incorrect'
            return render(request,'index.html',{'ownerdata':ownerdata})

        

        
    else:
        return render(request,'index.html')


    

 
    


