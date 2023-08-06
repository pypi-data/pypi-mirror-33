# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.models.get_enabled_signature_key_response

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io )
"""


class GetEnabledSignatureKeyResponse(object):

    """Implementation of the 'Get enabled signature key response' model.

    TODO: type model description here.

    Attributes:
        key_id (string): TODO: type description here.
        cipher (string): TODO: type description here.
        digest (string): TODO: type description here.
        created (string): TODO: type description here.
        enabled (bool): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "key_id":'key_id',
        "cipher":'cipher',
        "digest":'digest',
        "created":'created',
        "enabled":'enabled'
    }

    def __init__(self,
                 key_id=None,
                 cipher=None,
                 digest=None,
                 created=None,
                 enabled=None):
        """Constructor for the GetEnabledSignatureKeyResponse class"""

        # Initialize members of the class
        self.key_id = key_id
        self.cipher = cipher
        self.digest = digest
        self.created = created
        self.enabled = enabled


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
        cipher = dictionary.get('cipher')
        digest = dictionary.get('digest')
        created = dictionary.get('created')
        enabled = dictionary.get('enabled')

        # Return an object of this model
        return cls(key_id,
                   cipher,
                   digest,
                   created,
                   enabled)


