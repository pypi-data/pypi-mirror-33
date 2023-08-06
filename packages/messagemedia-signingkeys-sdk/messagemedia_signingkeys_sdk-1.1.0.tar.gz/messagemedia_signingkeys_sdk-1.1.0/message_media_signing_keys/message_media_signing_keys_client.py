# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.message_media_signing_keys_client

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""
from .decorators import lazy_property
from .configuration import Configuration
from .controllers.signature_key_management_controller import SignatureKeyManagementController

class MessageMediaSigningKeysClient(object):

    config = Configuration

    @lazy_property
    def signature_key_management(self):
        return SignatureKeyManagementController()


    def __init__(self, 
                 basic_auth_user_name = None,
                 basic_auth_password = None):
        if basic_auth_user_name != None:
            Configuration.basic_auth_user_name = basic_auth_user_name
        if basic_auth_password != None:
            Configuration.basic_auth_password = basic_auth_password


