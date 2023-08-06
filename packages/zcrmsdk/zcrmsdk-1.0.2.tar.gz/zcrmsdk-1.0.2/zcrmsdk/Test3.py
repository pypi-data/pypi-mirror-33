'''
Created on Jul 2, 2018

@author: sumanth-3058
'''
try:
    from .RestClient import ZCRMRestClient
    from .Operations import ZCRMModule, ZCRMRecord,\
    ZCRMUser, ZCRMInventoryLineItem, ZCRMTax, ZCRMJunctionRecord, ZCRMNote,\
    ZCRMCustomView, ZCRMRole, ZCRMProfile,ZCRMCustomFunction
    from .OAuthClient import ZohoOAuth
    from .CLException import ZCRMException
    from .Utility import APIConstants
    from .Org import ZCRMOrganization
except ImportError:
    print("\n\n:::::ERRO::::")
    from RestClient import ZCRMRestClient
    print("\n\n:::::OK::::")
    from Operations import ZCRMModule, ZCRMRecord,\
    ZCRMUser, ZCRMInventoryLineItem, ZCRMTax, ZCRMJunctionRecord, ZCRMNote,\
    ZCRMCustomView, ZCRMRole, ZCRMProfile,ZCRMCustomFunction
    from OAuthClient import ZohoOAuth
    from CLException import ZCRMException
    from Utility import APIConstants
    from Org import ZCRMOrganization
import threading,requests

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def test(self):
        if 1==1:
            pass
        zcrmsdk.RestClient.ZCRMRestClient.get_instance().initialize()
        print(zcrmsdk.RestClient.ZCRMRestClient.get_instance().get_all_modules())
        
obj=MyClass();
threading.current_thread().setName('sumanth.chilka@zohocorp.com')
obj.test();