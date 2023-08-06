# -*- coding: utf-8 -*-

"""
    tests.controllers.test_signature_key_management_controller

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""

import jsonpickle
import dateutil.parser
from .controller_test_base import ControllerTestBase
from ..test_helper import TestHelper
from message_media_signing_keys.api_helper import APIHelper
from message_media_signing_keys.models.create_signature_key_request import CreateSignatureKeyRequest


class SignatureKeyManagementControllerTests(ControllerTestBase):

    @classmethod
    def setUpClass(cls):
        super(SignatureKeyManagementControllerTests, cls).setUpClass()
        cls.controller = cls.api_client.signature_key_management

    # Todo: Add description for test test_create_signature_key_test
    def test_create_signature_key_test(self):
        # Parameters for the API call
        body = APIHelper.json_deserialize('{"digest":"SHA224","cipher":"RSA"}', CreateSignatureKeyRequest.from_dictionary)

        # Perform the API call through the SDK function
        result = self.controller.create_signature_key(body)

        # Test response code
        self.assertEquals(self.response_catcher.response.status_code, 201)
        
        # Test whether the captured response is as we expected
        self.assertIsNotNone(result)
        expected_body = APIHelper.json_deserialize(
            '{"key_id":"7ca628a8-08b0-4e42-aeb8-960b37049c31","public_key":"MIGfMA0GCSq'
            'GSIb3DQEBAQUAA4GNADCBiQKBgQCTIxtRyT5CuOD74r7UCT+AKzWNxvaAP9myjAqR7+vBnJKEvo'
            'PnmbKTnm6uLlxutnMbjKrnCCWnQ9vtBVnnd+ElhwLDPADfMcJoOqwi7mTcxucckeEbBsfsgYRfd'
            'acxgSZL8hVD1hLViQr3xwjEIkJcx1w3x8npvwMuTY0uW8+PjwIDAQAB","cipher":"RSA","di'
            'gest":"SHA224","created":"2018-01-18T10:16:12.364Z","enabled":false}'
            )
        received_body = APIHelper.json_deserialize(self.response_catcher.response.raw_body)
        self.assertTrue(TestHelper.match_body(expected_body, received_body))


