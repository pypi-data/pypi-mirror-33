"""Responsys REST API Client."""
# used to issue CRUD requests, the meat and 'taters of this thing
import requests
# used with the login with certificate functions
# import base64 as base64

# Interact API returns a lot of json-like text objects
# we use this to bind them to python objects
import json

# used with the login with certificate functions
# from random import choice

# used with the login with certificate functions
# from string import ascii_uppercase

# our own rules for data objects.
from .containers import rules

# Helper functions for use with direct implementations of calls as below

# # Helps with Login with username and certificates
# def generate_client_challenge_value(length=16):
#     return base64.b64encode(
#         bytes(''.join(choice(ascii_uppercase) for i in range(16)), 'utf-8')
#     )

class Client:
    """The main client."""

    def __init__(self, config, creds):
        """Initialize."""
        self.config = config
        self.creds = creds

    """Internal methods."""

    def _login(self, user_name, password, url):
        """Login with username and password."""
        data = {
            "user_name": user_name,
            "password": password,
            "auth_type": "password"
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        return requests.post(url, data=data, headers=headers)


    def _login_with_username_and_certificates(self, url, user_name):
        """Login with username and certificates."""
        # # TODO: Implement
        # # Step 1 - Authenticate server by sending the following REST request
        # data = {
        #     "user_name" : user_name,
        #     "auth_type" : "server",
        #     "client_challenge" : client_challenge_value
        # }
        # service_url = 'auth/token'
        # url = url + service_url
        # client_challenge_value = generate_client_challenge_value()

        # # Step 2 - Get response from the server and decrypt with RSA and
        # # Public Key Certificate (downloaded from Interact interface)
        # response = requests.post(url, data=data, headers=headers)
        # # TODO: Implement parse response
        # # Expect:
        # # {
        # #     "authToken" : "<TEMP_AUTH_TOKEN>",
        # #     "serverChallenge" : "<BASE_64_ENCODED_SERVER_CHALLENGE>",
        # #     "clientChallenge" : "<ENCRYPTED_AND_THEN_BASE_64_ENCODED_CLIENT_CHALLENGE>"
        # # }
        # response = parse_response()
        # # TODO: Implement import certificate
        # certificate = import_local_public_key_certificate(file)
        # # TODO: Implement RSA decryption
        # response = decrypt(response)
        # # TODO: Implement authorize call
        # response = login_with_username_and_certificate_authorization(
        #     user_name,
        #     auth_type=client,
        #     server_challenge=encrypt(response["serverChallenge"])
        # )

        # return response
        raise(NotImplementedError)

    def _get_context(self):
        """
        Return the login response as context.

        Used with each individual call to Responsys API.
        """
        context = json.loads(
            self._login(
                self.creds.user_name,
                self.creds.password,
                self.config.login_url
            ).text
        )
        context['api_url'] = self.config.api_url
        return context

    def _refresh_token(self, token):
        """Refresh the token. Called when it's expired."""
        # # TODO: Implement
        # # Refresh token
        # def refresh_token(url, old_auth_token):
        #     service_url = 'auth/token'
        #     url = url + service_url
        #     data = {'auth_type' : 'token'}
        #     headers = {'Authorization' : auth_token}
        #     response = requests.post(url, data=data, headers=headers)
        #     return response


    """Interal helper methods."""

    def _list_child(self, child, from_type):
        if type(child) is from_type:
            parent = []
            parent.append(child)
            return parent
        else:
            return child


    def _nonstr_to_str(self, data):
        # Quietly convert bytes to strings... I'm uneasy about this
        if type(data) is bytes:
            data = data.decode('utf-8')
        # Convert other types to strings because Responsys ignores most of them
        if type(data) in [int, float, bool, dict, list, set, tuple, type(None)]:
            data = str(data)
        return data


    def _post(self, service_url, data, **kwargs):
        context = self._get_context()
        data = json.dumps(data)
        headers = {
            'Authorization': context["authToken"],
            'Content-Type': 'application/json'
        }
        endpoint = '{e}/{a}/{s}'.format(
            e=context["endPoint"],
            a=context["api_url"],
            s=service_url)
        response = requests.post(data=data, headers=headers, url=endpoint)
        try:
            response = json.loads(response.text)
        except:
            pass
        return response

    def _delete(self, service_url):
        context = self._get_context()
        headers = {'Authorization': context["authToken"]}
        endpoint = '{e}/{a}/{s}'.format(
            e=context["endPoint"],
            a=context["api_url"],
            s=service_url)
        response = requests.delete(url=endpoint, headers=headers)
        try:
            response = json.loads(response.text)
        except:
            pass
        return response

    def _trim_path(self, path):
        # chop trailing slash
        try:
            if path[-1] == '/':
                path = path[:-1]
            # chop leading slash
            if path[0] == '/':
                path = path[1:]
        except:
            pass
        return path


    def _prep_doc_and_path(
        self,
        document,
        local_path=None,
        remote_path=None
    ):
        if local_path is None:
            local_path = self.config.remote_content_library_folder
        local_path = self._trim_path(local_path)
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        document_data = open(f'{local_path}/{document}', 'r').read()
        # just use the filename, omit the path
        document_name = document.split('/')[-1]
        if document_name.endswith('.html'):
            raise ValueError("""
.html is not allowed in Responsys Interact.
It would silently rename your .html files to .htm on upload.
Instead the Responsys Interact Python wrapper library doesn't allow it.
Rename your .html files to .htm before you upload them.
This will prevent mismatches and chaos.
You will be happy you did.
                """)
        data = {
            'documentPath': '/contentlibrary/{p}/{d}'.format(
                p=remote_path, d=document_name),
            'content': document_data
        }
        return {'data': data, 'document_name': document_name, 'remote_path': remote_path}

    """Direct implentations of calls from Responsys Interact REST API documentation
    https://docs.oracle.com/cloud/latest/marketingcs_gs/OMCEB/OMCEB.pdf
    All comment descriptions are directly from the v1.3 REST API documentation,
    except some English-language grammar and syntax inconsistencies are
    modified from their documentation and code-comment style to match PEP-8.
    """

    """Main functions."""

    def get_profile_lists(self):
        """Retrieving all profile lists for an account."""
        return self._get('lists')

    def update_profile_list(self,
                            list_name,
                            fields,
                            records,
                            html_value='H',
                            optin_value='I',
                            text_value='T',
                            insert_on_no_match=True,
                            insert_on_match='REPLACE_ALL',
                            match_column_name1='RIID_',
                            match_column_name2=None,
                            match_operator='NONE',
                            opt_out_value='O',
                            reject_records_if_channel_empty=None,
                            default_permission_status='OPTIN'):
        """Merge or update members in a profile list table."""

        # Fields, records to lists to accept str arg for single record updates
        fields = self._list_child(fields, str)
        records = self._list_child(records, str)

        # Clean non string objects from fields
        if self.config.caste_nonstr_to_str == True:
            try:
                fields = [self._nonstr_to_str(f) for f in fields]
            except:
                pass

            # Clean non string from records
            try:
                records = [self._nonstr_to_str(r) for r in records]
            except:
                pass


        data = {
            'recordData': {
                'fieldNames': fields,
                'records': [
                    records
                ],
                'mapTemplateName': None
            },
            'mergeRule': {
                'htmlValue': html_value,
                'optinValue': optin_value,
                'textValue': text_value,
                'insertOnNoMatch': insert_on_no_match,
                'updateOnMatch': insert_on_match,
                'matchColumnName1': match_column_name1,
                'matchColumnName2': match_column_name2,
                'matchOperator': match_operator,
                'optoutValue': opt_out_value,
                'rejectRecordIfChannelEmpty': reject_records_if_channel_empty,
                'defaultPermissionStatus': default_permission_status
            }
        }
        service_url = 'lists/{list_name}/members'.format(list_name=list_name)
        return self._post(service_url, data)
        # raise(NotImplementedError)

    def _get(self, service_url, **kwargs):
        """General purpose build for GET requests to Interact API."""
        context = self._get_context()
        endpoint = '{e}/{a}/{s}'.format(
            e=context["endPoint"],
            a=context["api_url"],
            s=service_url)
        headers = kwargs.get('headers', {'Authorization': context['authToken']})
        # use parameters if we got them
        if "parameters" in kwargs:
            parameters = kwargs.get('parameters', None)
            endpoint = '{e}?{p}'.format(e=endpoint, p=parameters)
        response = requests.get(url=endpoint, headers=headers)
        try:
            response = json.loads(response.text)
        except:
            pass
        return response

    def get_campaigns(self):
        """Get all EMD email campaigns."""
        return self._get('campaigns')

    def get_push_campaigns(self):
        """Get all Push campaigns."""
        return self._get('campaigns?type=push')

    def get_member_of_list_by_riid(
        self,
        list_name,
        riid,
        fields_to_return=['all']
    ):
        """Retrieve a member of a profile list using RIID."""
        service_url = 'lists/{l}/members/{id}'.format(l=list_name, id=riid)
        parameters = 'fs={fs}'.format(fs=",".join(fields_to_return))
        return self._get(service_url, parameters=parameters)

    def get_member_of_list_by_attribute(
        self,
        list_name,
        record_id,
        query_attribute='c',
        fields_to_return=['all']
    ):
        """Retrieve a member of a profile list based on query attribute."""
        service_url = 'lists/{l}/members'.format(l=list_name)
        parameters = 'fs={fs}&qa={qa}&id={id}'.format(
            fs=",".join(fields_to_return),
            qa=query_attribute,
            id=record_id)
        return self._get(service_url, parameters=parameters)

    def get_profile_extensions_for_list(self, list_name):
        """Retrieve all profile extensions of a profile list."""
        return self._get('lists/{l}/listExtensions'.format(l=list_name))

    def get_member_of_profile_extension_by_riid(
        self,
        list_name,
        pet_name,
        riid,
        fields_to_return=['all']
    ):
        """Retrieve a member of a profile extension table based on RIID."""
        service_url = 'lists/{l}/listExtensions/{p}/members/{id}'.format(
            l=list_name,
            p=pet_name,
            id=riid)
        parameters = 'fs={fs}'.format(fs=",".join(fields_to_return))
        return self._get(service_url, parameters=parameters)

    def get_member_of_profile_extension_by_attribute(
        self,
        list_name,
        pet_name,
        record_id,
        query_attribute='c',
        fields_to_return=['all']
    ):
        """Retrieve a member of a profile extension table based on a query attribute."""
        service_url = 'lists/{l}/listExtensions/{p}/members'.format(
            l=list_name,
            p=pet_name)
        parameters = 'fs={fs}&qa={qa}&id={id}'.format(
            fs=",".join(fields_to_return),
            qa=query_attribute,
            id=record_id)
        return self._get(service_url, parameters=parameters)

    def get_lists_for_record(self, riid):
        """Find what lists a record is in by RIID."""
        all_lists = [list_name["name"] for list_name in self.get_profile_lists()]
        # container list
        member_of = []
        for profile_list in all_lists:
            response = self.get_member_of_list_by_riid(
                self, profile_list, riid)
            # if the member (by riid) is in the profile list
            # add it to the list of all profile lists
            if "recordData" in response:
                member_of.append(profile_list)
        return member_of

    def send_email_message(
            self,
            recipients,
            folder_name,
            campaign_name,
            optional_data={}):
        """Trigger email message."""
        # Accept a string for one recipient but work with a list either way.
        recipients = self._list_child(recipients, str)
        if type(recipients) is not list:
            raise TypeError(
                'Recipients data must be a string of one recipient or a list.')
        # Accept a dict for one recipient's optional data
        # but work with a list either way.
        optional_data = self._list_child(optional_data, dict)
        optional_data = [
            {
                self._nonstr_to_str(k):self._nonstr_to_str(v) for k,v in d.items()
            } for d in optional_data
        ]
        # then if there's no optional data extend it out so we can zip it up
        if optional_data == [{}] and len(recipients) > 1:
            optional_data = optional_data * len(recipients)
        if type(optional_data) is not list:
            raise TypeError(
                'Recipients data must be a dictionary of key/value pairs for\n'+
                'one recipient or a list of dictionaries for multiple recipients')
        if len(recipients) != len(optional_data):
            raise ValueError(
                'Recipients list must be same length as optional data list')
        zipped = zip(recipients, optional_data)
        data = {
            "recipientData" : [
                {
                    "recipient" : {
                        "customerId" : None,
                        "emailAddress" : recipient[0],
                        "listName" : {
                            "folderName" : folder_name,
                            "objectName" : campaign_name
                        },
                        "recipientId" : None,
                        "mobileNumber" : None,
                        "emailFormat" : "HTML_FORMAT"
                    },
                    "optionalData" : [
                        {} if len(d.items()) is 0 else {
                            "name": list(d.keys())[0],
                            "value": list(d.values())[0]
                        } for d in self._list_child(recipient[1], dict)
                    ]
                } for recipient in zipped
            ]
        }
        service_url = 'campaigns/{c}/email'.format(c=campaign_name)
        return self._post(service_url, data)

    def delete_from_profile_list(self, list_name, riid):
        """Delete Profile List Recipients based on RIID."""
        service_url = 'lists/{l}/members/{id}'.format(l=list_name, id=riid)
        return self._delete(service_url)

    def delete_member_of_profile_extension_by_riid(
        self,
        list_name,
        pet_name,
        riid
    ):
        """Delete a member of a profile extension table based on RIID."""
        service_url = 'lists/{l}/listExtensions/{p}/members/{id}'.format(
            l=list_name,
            p=pet_name,
            id=riid)
        return self._delete(service_url)

    def create_supplemental_table(
        self,
        supplemental_table_name,
        folder_name='',
        fields='',
        default_field_type='STR500',
        data_extraction_key=None,
        primary_key=None
    ):
        """Create a new supplemental table."""
        if type(fields) == str:
            raise TypeError('Fields must be a list.')
        if folder_name == '':
            folder_name = self.config.api_folder
        service_url = 'folders/{f}/suppData'.format(f=folder_name)
        if primary_key is None:
            try:
                primary_key = fields[0]
            except ValueError:
                raise ValueError(
                    """Cannot create supplemental table with no fields.
                    Primary key field is required.""")
        data = {
            # TODO: Use field types per field
            "table": {"objectName": supplemental_table_name},
            "fields": [
                {
                    "fieldName": field,
                    "fieldType": default_field_type,
                    "dataExtractionKey": False
                } for field in fields
            ],
            "primaryKeys": [primary_key]
        }
        return self._post(service_url, data)

    def list_folder(
        self,
        remote_path=None,
        object_type='all'
    ):
        """List the contents of a folder."""
        valid_types = ['all', 'folders', 'docs', 'items']
        if object_type not in valid_types:
            raise ValueError(
                """Object type must be one of {v}.""".format(
                    v=str(valid_types)[1:-1])
                )
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        service_url = 'clFolders/contentlibrary/{f}?type={o}'.format(
            f=remote_path, o=object_type)
        return self._get(service_url)

    def create_folder(
        self,
        remote_path=None
    ):
        """Create a new folder in /contentlibrary/."""
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        service_url = 'clFolders'
        data = {
            "folderPath": '/contentlibrary/{f}'.format(f=remote_path)
        }
        return self._post(service_url, data)

    def create_document(
        self,
        document,
        local_path=None,
        remote_path=None
    ):
        """Create a document in /contentlibrary/."""
        if local_path is None:
            local_path = self.config.local_content_library_folder,
        local_path = self._trim_path(local_path)
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        service_url = 'clDocs'
        data = self._prep_doc_and_path(
            document, local_path, remote_path)['data']
        return self._post(service_url, data)

    def get_document(
        self,
        document,
        remote_path=None
    ):
        """Get a document from /contentlibrary/."""
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        service_url = 'clDocs/contentlibrary/{rfp}/{d}'.format(
            rfp=remote_path,
            d=document)
        return self._get(service_url)

    # def update_document(
    #     self,
    #     document,
    #     local_path=None,
    #     remote_path=None
    # ):
    #     # print(local_path, remote_path, document)
    #     # input()
    #     """Update a document that's already in /contentlibrary/."""
    #     # print(type(local_path), local_path)
    #     # if local_path is None:
    #     #     print(type(local_path), local_path)
    #     #     local_path = self.config.local_content_library_folder,
    #     #     print(type(local_path), local_path)
    #     # local_path = self._trim_path(local_path)
    #     if remote_path is None:
    #         remote_path = self.config.remote_content_library_folder
    #     remote_path = self._trim_path(remote_path)
    #     # print(type(local_path), local_path, remote_path, document)
    #     # input()
    #     prepped = self._prep_doc_and_path(
    #         document, local_path, remote_path)
    #     print(prepped)
    #     service_url = 'clDocs/contentlibrary/{rfp}/{p}'.format(
    #         rfp=remote_path,
    #         p=prepped["document_name"])
    #     print(service_url)
    #     input()
    #     return self._post(service_url, {prepped['data']['content']})
        # return


    def delete_document(self, document, remote_path=None):
        """Delete a document in /contentlibrary/'."""

        # # First try to get the document before we delete it!
        # self.get_document(document, remote_path)

        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
        remote_path = self._trim_path(remote_path)
        service_url = 'clDocs/contentlibrary/{p}/{d}'.format(
            p=remote_path, d=document)
        return self._delete(service_url)

    def delete_folder(self, remote_path=None):
        """Delete a folder in /contentlibrary/."""
        if remote_path is None:
            remote_path = self.config.remote_content_library_folder
            remote_path = self._trim_path(remote_path)
        remote_path = self._trim_path(remote_path)
        service_url = 'clFolders/contentlibrary/{f}'.format(f=remote_path)
        return self._delete(service_url)






    # NOT IMPLEMENTED GROUP

    def create_profile_extension(self, profile_extension_name, records):
        """Create a profile extension table."""

    def update_profile_extension(self, profile_extension_name, records):
        """Update a profile extension table."""
        raise(NotImplementedError)

    def update_supplemental_table(self, supplemental_table_name, records):
        """Update a supplemental table."""
        raise(NotImplementedError)

    def get_record_from_supplemental_table(self, supplemental_table_name, record):
        """Get a record from a supplemental table."""
        raise(NotImplementedError)

    def delete_record_from_supplemental_table(self, supplemental_table_name, record):
        """Delete a record from a supplemental table."""
        raise(NotImplementedError)

    def update_list_and_send_email_message(
        self, list, recipients, campaign_name
    ):
        """Update a list and then send an email message."""
        raise(NotImplementedError)

    def update_list_and_send_email_message_with_attachments(
        self, list, recipeints, campaign_name, attachments
    ):
        """Update a list and send an email message."""
        raise(NotImplementedError)

    def update_list_and_send_sms(self, list, recipients, campaign_name):
        """Update a list and send an sms."""
        raise(NotImplementedError)

    def send_push_message(self, campaign_name, recipient_id):
        """Send a push message."""
        raise(NotImplementedError)

    def trigger_custom_event(self, event_name):
        """Trigger a custom event."""
        raise(NotImplementedError)

    def schedule_campaign(self, campaign_name, schedule):
        """Schedule a campaign."""
        raise(NotImplementedError)

    def get_schedules_for_campaign(self, campaign_name):
        """Get the schedule IDs for a campaign."""
        raise(NotImplementedError)

    def get_campaign_schedule(self, campaign_name):
        """Get the schedule for a campaign."""
        raise(NotImplementedError)

    def update_campaign_schedule(self, campaign_name):
        """Update a campaign schedule."""
        raise(NotImplementedError)

    def unschedule_campaign(self, campaign_name):
        """Unschedule a campaign."""
        raise(NotImplementedError)

    def create_media_file(self, path_to_media_file, media_file):
        """Create a media file."""
        raise(NotImplementedError)

    def get_media_file(self, path_to_media_file):
        """Get a media file."""
        raise(NotImplementedError)

    def update_media_file(self, path_to_old_media_file, new_media_file):
        """Update a media file."""
        raise(NotImplementedError)

    def delete_media_file(self, path_to_media_file):
        """Delete a media file."""
        raise(NotImplementedError)

    def copy_media_file(self, path_to_media_file, new_name=None):
        """Copy a media file."""
        raise(NotImplementedError)

    def set_images_in_document(self, path_to_interact_document, images):
        """Set the image data for media that are referenced in a document."""
        raise(NotImplementedError)

    def get_images_in_document(self, path_to_interact_document):
        """Get the image data for media that are referenced in a document."""
        raise(NotImplementedError)
