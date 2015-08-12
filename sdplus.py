__version__ = '1.1'
# http://nbsvr241:8080/SetUpWizard.do?SkipNV2Filter=true&forwardTo=api

import requests
from xml.dom import minidom


class API:
    """
    The main sending class for the Manage Service Engine API
    """
    def __init__(self, username, password, domain, auth_type, api_url):
        self.login_params = {
            'username': username,
            'password': password,
            'DOMAIN_NAME': domain,
            'logonDomainName': auth_type,  # 'AD_AUTH' or 'Local Authentication'
        }
        self.api_url = api_url

    def _send(self, params):
        """
        Send through details into API
        :param params: Specific attributes of request (Detailed in API documentation)
        :return: status, dict (of response)
        """
        params.update(self.login_params)
        raw_xml = requests.get(self.api_url, params).text
        xml_response = minidom.parseString(raw_xml)
        # print(xml_response.toprettyxml())
        status = xml_response.getElementsByTagName("operationstatus")[0].firstChild.wholeText
        message = xml_response.getElementsByTagName("message")[0].firstChild.wholeText
        details = {
            'status': status
            , 'message': message
        }
        if status == "Success":
            details_element = xml_response.getElementsByTagName("propname")
            if details_element:
                propname_keys = dict(
                    (item.getAttribute('key'), item.firstChild.data)
                    for item in details_element if item.firstChild is not None
                )
                details.update(propname_keys)
            returned_id = xml_response.getElementsByTagName("workorderid")
            if returned_id:
                details['workorderid'] = returned_id[0].firstChild.wholeText
        return details


class Request(API):
    def __init__(self, username, password, domain, auth_type):
        api_url = 'http://nbsvr241:8080/servlets/RequestServlet'  # Test
        # api_url = 'http://sdplus/servlets/RequestServlet'  # Live
        API.__init__(username, password, domain, auth_type, api_url)

    # Add Request
    def add(self,
            subject,
            description,
            requester,
            requesteremail,
            impact='3 Impacts Department',
            urgency='3 Business Operations Slightly Affected',
            subcategory='Other',
            reqtemplate='Default Request',
            requesttype='Service Request',
            status='',
            mode='@Southmead Brunel building',
            service='CERNER',
            category='',
            group='Back Office Third Party',
            technician='',
            technicianemail='',
            item='',
            impactdetails='',
            resolution='',
            priority='',
            level='',
            supplier_ref=''):
        params = {
            'operation': 'addrequest',
            'subject': subject,
            'description': description,
            'requester': requester,
            'impact': impact,
            'urgency': urgency,
            'subcategory': subcategory,
            'requesteremail': requesteremail,
            'reqtemplate': reqtemplate,
            'requesttype': requesttype,
            'status': status,
            'mode': mode,  #=site
            'service': service,    #=Service Category
            'category': category,  #''=Self Service Incident
            'group': group,
            'technician': technician,
            'technicianemail': technicianemail,
            'item': item,
            'impactdetails': impactdetails,
            'resolution': resolution,
            'priority': priority,
            'level': level,
            'supplier ref': supplier_ref
        }
        return self._send(params)

    # Update a call
    def update(self,
            workorderid,
            reqtemplate='',
            requesttype='',
            subject='',
            description='',
            resolution='',
            requester='',
            requesteremail='',
            priority='',
            level='',
            status='',
            impact='',
            urgency='',
            impactdetails='',
            mode='',
            service='',
            category='',
            subcategory='',
            item='',
            group='',
            technician='',
            technicianemail='',
            supplierRef=''):
        params = {
            'operation': 'UpdateRequest',
            'workOrderID': workorderid,
            'reqtemplate': reqtemplate,
            'requesttype': requesttype,
            'subject': subject,
            'description': description,
            'resolution': resolution,
            'requester': requester,
            'requesteremail': requesteremail,
            'priority': priority,
            'level': level,
            'status': status,
            'impact': impact,
            'urgency': urgency,
            'impactdetails': impactdetails,
            'mode': mode,
            'service': service,
            'category': category,
            'subcategory': subcategory,
            'item': item,
            'group': group,
            'technician': technician,
            'technicianemail': technicianemail,
            'supplier ref': supplierRef
        }
        return self._send(params)

    def assign(self, work_order_id, technician):
        return self.update(work_order_id, technician=technician)

    def close(self, work_order_id, close_comments=''):
        params = {
            'operation': 'CloseRequest',
            'workOrderID': work_order_id,
            'closecomment': close_comments
        }
        return self._send(params)

    def delete(self, workorderid):   #get dictionary of a call's details
        params = {
            'operation': 'deleterequest',
            'workOrderID': workorderid
        }
        return self._send(params)

    def add_note(self, workorderid, notesText, isPublic=True):
        params = {
            'operation': 'AddNotes',
            'workOrderID': workorderid,
            'notesText': notesText,
            'isPublic': isPublic   # True=public notes, False=private notes
        }
        return self._send(params)

    def add_work_log(self,
            workorderid,
            technician='',
            technicianemail='',
            description='',
            workhours='',
            workminutes='',
            cost='',
            executedtime=''):
        params = {
            'operation': 'AddNotes',
            'workOrderID': workorderid,
            'technician': technician,
            'technicianemail': technicianemail,
            'description': description,
            'workhours': workhours,
            'workminutes': workminutes,
            'cost': cost,
            'executedtime': executedtime,
        }
        return self._send(params)

    def delete_work_log(self, workorderid, workLogID=''):
        params = {
            'operation': 'deleteworklog',
            'workOrderID': workorderid,
            'requestchargeid': workLogID,    #work Log ID to delete
        }
        return self._send(params)

    def get(self, workorderid):   #get dictionary of a call's details
        params = {
            'operation': 'getrequestdetails',
            'workOrderID': workorderid
        }
        return self._send(params)


class Requester(API):
    def __init__(self, username, password, domain, auth_type):
        api_url = 'http://nbsvr241:8080/servlets/RequesterServlet'  # Test
        # api_url = 'http://sdplus/servlets/RequesterServlet'  # Live
        API.__init__(self, username, password, domain, auth_type, api_url)

    def add(self,
            name,
            employee_id='',
            description='',
            email='',
            phone='',
            mobile='',
            site='',
            department_name='',
            job_title='',
            request_view_permission='',
            approve_purchase_order='',
            login_name='',
            pwd='',
            udf_aliases={}  # {'udf_column_name_1': 'value1', 'udf_column_name_2': 'value2'}
            ):
        params = {
            'operation': 'AddRequester',
            'name': name,
            'employeeId': employee_id,
            'description': description,
            'email': email,
            'phone': phone,
            'mobile': mobile,
            'site': site,
            'departmentName': department_name,
            'jobTitle': job_title,
            'requestViewPermission': request_view_permission,
            'approvePurchaseOrder': approve_purchase_order,
            'loginName': login_name,
            'pwd': pwd
        }
        if udf_aliases:
            params.update(udf_aliases)
        return self._send(params)

    def update(self,
               req_login_name,
               req_domain_name='',
               req_user_name='',
               req_email_id='',
               name='',
               user_id='',
               employee_id='',
               email='',
               phone='',
               mobile='',
               sms_mail_id='',
               site='',
               department_name='',
               job_title='',
               request_view_permission='',
               approve_purchase_order='',
               udf_aliases={}  # {'udf_column_name_1': 'value1', 'udf_column_name_2': 'value2'}
               ):
        params = {
            'operation': 'UpdateRequester',
            'reqLoginName': req_login_name,
            'reqDomainName': req_domain_name,
            'reqUserName': req_user_name,
            'reqEmailId': req_email_id,
            'name': name,
            'userid': user_id,
            'employeeId': employee_id,
            'email': email,
            'phone': phone,
            'mobile': mobile,
            'smsMailId': sms_mail_id,
            'site': site,
            'departmentName': department_name,
            'jobTitle': job_title,
            'requestViewPermission': request_view_permission,
            'approvePurchaseOrder': approve_purchase_order
        }
        if udf_aliases:
            params.update(udf_aliases)
        return self._send(params)

    def delete(self,
               req_login_name='',
               req_user_name='',
               req_domain_name='',
               req_email_id='',
               user_id='',
               username='',
               password=''
               ):
        params = {
            'operation': 'DeleteRequester',
            'reqLoginName': req_login_name,
            'reqUserName': req_user_name,
            'reqDomainName': req_domain_name,
            'reqEmailId': req_email_id,
            'userid': user_id,
            'username': username,
            'password': password
        }
        return self._send(params)


def example():
    import os
    api_requester = Requester(os.environ.get("USERNAME"), '<PASSWORD>', 'NORTHBRISTOL', 'AD_AUTH')
    details = api_requester.update('nbe0365', req_domain_name='NORTHBRISTOL',
                                   udf_aliases={'Memorable Word': 'changed to new item'})
    print(details)

example()
