# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.models.get_signature_key_list_403_response_exception

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io )
"""
from ..api_helper import APIHelper
import message_media_signing_keys.exceptions.api_exception

class GetSignatureKeyList403ResponseException(message_media_signing_keys.exceptions.api_exception.APIException):
    def __init__(self, reason, context):
        """Constructor for the GetSignatureKeyList403ResponseException class

        Args:
            reason (string): The reason (or error message) for the Exception
                to be raised.
            context (HttpContext):  The HttpContext of the API call.

        """
        super(GetSignatureKeyList403ResponseException, self).__init__(reason, context)
        dictionary = APIHelper.json_deserialize(self.context.response.raw_body)
        if isinstance(dictionary, dict):
            self.unbox(dictionary)

    def unbox(self, dictionary):
        """Populates the properties of this object by extracting them from a dictionary.

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        """
        self.message = dictionary.get('message')
