# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.models.enable_signature_key_request

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io )
"""


class EnableSignatureKeyRequest(object):

    """Implementation of the 'Enable signature key request' model.

    TODO: type model description here.

    Attributes:
        key_id (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "key_id":'key_id'
    }

    def __init__(self,
                 key_id=None):
        """Constructor for the EnableSignatureKeyRequest class"""

        # Initialize members of the class
        self.key_id = key_id


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        key_id = dictionary.get('key_id')

        # Return an object of this model
        return cls(key_id)


