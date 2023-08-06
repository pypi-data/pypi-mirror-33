# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.models.create_signature_key_request

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io )
"""


class CreateSignatureKeyRequest(object):

    """Implementation of the 'Create signature key request' model.

    TODO: type model description here.

    Attributes:
        digest (string): TODO: type description here.
        cipher (string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "digest":'digest',
        "cipher":'cipher'
    }

    def __init__(self,
                 digest=None,
                 cipher=None):
        """Constructor for the CreateSignatureKeyRequest class"""

        # Initialize members of the class
        self.digest = digest
        self.cipher = cipher


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
        digest = dictionary.get('digest')
        cipher = dictionary.get('cipher')

        # Return an object of this model
        return cls(digest,
                   cipher)


