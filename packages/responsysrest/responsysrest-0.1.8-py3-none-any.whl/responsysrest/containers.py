"""Containers to expose to client for rules and request processing."""
# TODO expose as a class with enums


class Mergable:
    """Class container for mergable lists."""

    def __init__(self, fields, records, merge_rules):
        if len(set([len(r) for r in records])) is not 1:
            raise ValueError("")

        if len(fields) == len(records):
            self.fields = fields
            self.records = records
        else:
            raise ValueError("Fields and records counts to not match.")
        self.merge_rules = merge_rules




rules = {
    'update_profile_list':
        [
            {
                'recordData': {
                    'fieldNames': [
                        'email_address_'
                        '''
                        #'riid_',
                        #'mobile_number_',
                        #'email_address_'
                        '''
                    ],
                    'records': [
                        [
                            'a@b.c'
                            '''
                            #'0123456', # RIID_
                            #'0123456789', # US Ten-digit phone w/o dashes
                            #'a@b.c' # email address
                            '''
                        ]
                    ],
                    'mergeTemplateName': None
                },
                'mergeRule': {
                    'htmlValue': {
                        'default': 'H',
                        'options': [
                            'H',
                            'h',
                            'HTML',
                            'html',
                            'Html',
                            'HTM',
                            'htm',
                            'Htm'
                        ]
                    },
                    'optinValue': {
                        'default': 'I',
                        'options': [
                            'I',
                            'i',
                            '1'
                        ]
                    },
                    'textValue': {
                        'default': 'T',
                        'options': [
                            'T',
                            't',
                            'TEXT',
                            'text',
                            'Text',
                            'TXT',
                            'txt',
                            'Txt'
                        ]
                    },
                    'insertOnNoMatch': {
                        'default': True,
                        'options': [
                            True,
                            False
                        ]
                    },
                    'updateOnMatch': {
                        'default': 'REPLACE_ALL',
                        'options': [
                            'NO_UPDATE',
                            'REPLACE_ALL'
                        ]
                    },
                    'matchColumnName1': {
                        'default': 'RIID_',
                        'options': [
                            'RIID_',
                            'CUSTOMER_ID_',
                            'EMAIL_ADDRESS_',
                            'MOBILE_NUMBER_',
                            'EMAIL_MD5_HASH_',
                            'EMAIL_SHA256_HASH_'
                        ]
                    },
                    'matchColumnName2': {
                        'default': None,
                        'options': [
                            None,
                            'RIID_',
                            'CUSTOMER_ID_',
                            'EMAIL_ADDRESS_',
                            'MOBILE_NUMBER_',
                            'EMAIL_MD5_HASH_',
                            'EMAIL_SHA256_HASH_'
                        ]
                    },
                    '''
                    # 'matchColumnName3': {
                    #     'default': None,
                    #     'options': [
                    #         None
                    #     ] # deprecated
                    # },
                    '''
                    'matchOperator': {
                        'default': 'NONE',
                        'options': [
                            'NONE',
                            'AND'
                        ]
                    },
                    'optoutValue': {
                        'default': 'O',
                        'options': [
                            'O',
                            'o',
                            '0'
                        ]
                    },
                    'rejectRecordIfChannelEmpty': {
                        'default': None,
                        'options': [
                            None,
                            # Email
                            'E',
                            # Mobile
                            'M',
                            # Postal address
                            'P',
                            # Email or Mobile
                            'E,M',
                            # Email or Postal
                            'E,P',
                            # Mobile or Email
                            'M,E',
                            # Mobile or Postal
                            'M,P',
                            # Email, Mobile or Postal
                            'E,M,P',
                            # Email, Postal or Mobile
                            'E,P,M',
                            # Mobile, Email or Postal
                            'M,E,P',
                            # Mobile, Postal or Email
                            'M,P,E',
                            # Postal, Email or Postal
                            'P,E,M',
                            # Postal, Mobile or Email
                            'P,M,E'
                        ]
                    },
                    'defaultPermissionStatus': {
                        'default': 'OPTIN',
                        'options': [
                            'OPTIN',
                            'OPTOUT'
                        ]
                    }
                }
            }
        ],
        # RIID, EMAIL_ADDRESS, CUSTOMER_ID, MOBILE_NUMBER
    'query_attributes_allowed': ['r', 'e', 'c', 'm']
}
