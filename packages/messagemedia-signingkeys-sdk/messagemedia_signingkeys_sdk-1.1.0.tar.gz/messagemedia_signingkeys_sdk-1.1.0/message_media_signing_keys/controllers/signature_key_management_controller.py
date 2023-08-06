# -*- coding: utf-8 -*-

"""
    message_media_signing_keys.controllers.signature_key_management_controller

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""

import logging
from .base_controller import BaseController
from ..api_helper import APIHelper
from ..configuration import Configuration
from ..http.auth.basic_auth import BasicAuth
from ..models.get_enabled_signature_key_response import GetEnabledSignatureKeyResponse
from ..models.enable_signature_key_response import EnableSignatureKeyResponse
from ..models.get_signature_key_list_response import GetSignatureKeyListResponse
from ..models.get_signature_key_detail_response import GetSignatureKeyDetailResponse
from ..models.create_signature_key_response import CreateSignatureKeyResponse
from ..exceptions.get_enabled_signature_key_403_response_exception import GetEnabledSignatureKey403ResponseException
from ..exceptions.enable_signature_key_400_response_exception import EnableSignatureKey400ResponseException
from ..exceptions.enable_signature_key_403_response_exception import EnableSignatureKey403ResponseException
from ..exceptions.get_signature_key_list_400_response_exception import GetSignatureKeyList400ResponseException
from ..exceptions.delete_signature_key_403_response_exception import DeleteSignatureKey403ResponseException
from ..exceptions.get_signature_key_detail_400_response_exception import GetSignatureKeyDetail400ResponseException
from ..exceptions.get_signature_key_detail_403_response_exception import GetSignatureKeyDetail403ResponseException
from ..exceptions.create_signature_key_400_response_exception import CreateSignatureKey400ResponseException

class SignatureKeyManagementController(BaseController):

    """A Controller to access Endpoints in the message_media_signing_keys API."""

    def __init__(self, client=None, call_back=None):
        super(SignatureKeyManagementController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)

    def delete_disable_the_current_enabled_signature_key(self):
        """Does a DELETE request to /v1/iam/signature_keys/enabled.

        Disable the current enabled signature key.
        A successful request for the ```disable the current enabled signature
        key.``` endpoint will return no content when successful.
        If there is an enabled key, it will be disabled; and the 204 status
        code is returned.
        If there is no key or no enabled key, the 204 status code is also
        returned.

        Returns:
            void: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_disable_the_current_enabled_signature_key called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_disable_the_current_enabled_signature_key.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys/enabled'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_disable_the_current_enabled_signature_key.')
            _request = self.http_client.delete(_query_url)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'delete_disable_the_current_enabled_signature_key')
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_enabled_signature_key(self):
        """Does a GET request to /v1/iam/signature_keys/enabled.

        Retrieve the currently enabled signature key.
        A successful request for the ```get enabled signature key``` endpoint
        will return a response body as follows:
        ```json
        {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31",
            "cipher": "RSA",
            "digest": "SHA224",
            "created": "2018-01-18T10:16:12.364Z",
            "enabled": true
        }
        ```
        *Note: If there is no enabled signature key, then an HTTP 404 Not
        Found response will be returned*

        Returns:
            GetEnabledSignatureKeyResponse: Response from the API. The detail
                of signature key.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_enabled_signature_key called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_enabled_signature_key.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys/enabled'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_enabled_signature_key.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_enabled_signature_key.')
            _request = self.http_client.get(_query_url, headers=_headers)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'get_enabled_signature_key')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_enabled_signature_key.')
            if _context.response.status_code == 404:
                raise GetEnabledSignatureKey403ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetEnabledSignatureKeyResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_enable_signature_key(self,
                                    body):
        """Does a PATCH request to /v1/iam/signature_keys/enabled.

        Enable a signature key using the key_id returned in the ```create
        signature key``` endpoint.
        There is only one signature key is enabled at the one moment in time.
        So if you enable the new signature key, the old one will be disabled.
        The most basic body has the following structure:
        ```json
        {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31"
        }
        ```
        The response body of a successful PATCH request to ```enable signature
        key``` endpoint will contain the ```enabled``` properties with the
        value is true as follows:
        ```json
        {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31",
            "cipher": "RSA",
            "digest": "SHA224",
            "created": "2018-01-18T10:16:12.364Z",
            "enabled": true
        }
        ```
        *Note: If an invalid or non-existent key_id parameter is specified in
        the request, then an HTTP 404 Not Found response will be returned*

        Args:
            body (EnableSignatureKeyRequest): TODO: type description here.
                Example: 

        Returns:
            EnableSignatureKeyResponse: Response from the API. The enabled
                signature key.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_enable_signature_key called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_enable_signature_key.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys/enabled'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_enable_signature_key.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_enable_signature_key.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'update_enable_signature_key')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_enable_signature_key.')
            if _context.response.status_code == 400:
                raise EnableSignatureKey400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            elif _context.response.status_code == 404:
                raise EnableSignatureKey403ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, EnableSignatureKeyResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_signature_key_list(self):
        """Does a GET request to /v1/iam/signature_keys.

        Retrieve the paginated list of signature keys.
        A successful request for the ```get signature key list``` endpoint
        will return a response body as follows:
        ```json
        [
          {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31",
            "cipher": "RSA",
            "digest": "SHA224",
            "created": "2018-01-18T10:16:12.364Z",
            "enabled": false
          }
        ]
        ```

        Returns:
            list of GetSignatureKeyListResponse: Response from the API. The
                list of signature keys.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_signature_key_list called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_signature_key_list.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_signature_key_list.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_signature_key_list.')
            _request = self.http_client.get(_query_url, headers=_headers)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'get_signature_key_list')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_signature_key_list.')
            if _context.response.status_code == 400:
                raise GetSignatureKeyList400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetSignatureKeyListResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_signature_key(self,
                             key_id):
        """Does a DELETE request to /v1/iam/signature_keys/{key_id}.

        Delete a signature key using the key_id returned in the ```create
        signature key``` endpoint.
        A successful request for the ```delete signature key``` endpoint will
        return an empty response body.
        *Note: If an invalid or non-existent key_id parameter is specified in
        the request, then an HTTP 404 Not Found response will be returned*

        Args:
            key_id (string): TODO: type description here. Example: 

        Returns:
            void: Response from the API. The signature key has been deleted.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_signature_key called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_signature_key.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys/{key_id}'
            _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
                'key_id': key_id
            })
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_signature_key.')
            _request = self.http_client.delete(_query_url)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'delete_signature_key')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_signature_key.')
            if _context.response.status_code == 404:
                raise DeleteSignatureKey403ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_signature_key_detail(self,
                                 key_id):
        """Does a GET request to /v1/iam/signature_keys/{key_id}.

        Retrieve the current detail of a signature key using the key_id
        returned in the ```create signature key``` endpoint.
        A successful request for the ```get signature key detail``` endpoint
        will return a response body as follows:
        ```json
        {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31",
            "cipher": "RSA",
            "digest": "SHA224",
            "created": "2018-01-18T10:16:12.364Z",
            "enabled": false
        }
        ```
        *Note: If an invalid or non-existent key_id parameter is specified in
        the request, then an HTTP 404 Not Found response will be returned*

        Args:
            key_id (string): TODO: type description here. Example: 

        Returns:
            GetSignatureKeyDetailResponse: Response from the API. The detail
                of signature key.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_signature_key_detail called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_signature_key_detail.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys/{key_id}'
            _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
                'key_id': key_id
            })
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_signature_key_detail.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_signature_key_detail.')
            _request = self.http_client.get(_query_url, headers=_headers)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'get_signature_key_detail')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_signature_key_detail.')
            if _context.response.status_code == 400:
                raise GetSignatureKeyDetail400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            elif _context.response.status_code == 404:
                raise GetSignatureKeyDetail403ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetSignatureKeyDetailResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_signature_key(self,
                             body):
        """Does a POST request to /v1/iam/signature_keys.

        This will create a key pair:
        - The ```private key``` stored in MessageMedia is used to create the
        signature.
        - The ```public key``` is returned and stored at your side to verify
        the signature in callbacks.
        You need to enable your signature key after creating.
        The most basic body has the following structure:
        ```json
        {
            "digest": "SHA224",
            "cipher": "RSA"
        }
        ```
        - ```digest``` is used to hash the message. The valid values for
        digest type are: SHA224, SHA256, SHA512
        - ```cipher``` is used to encrypt the hashed message. The valid value
        for cipher type is: RSA
        A successful request for the ```create signature key``` endpoint will
        return a response body as follows:
        ```json
        {
            "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31",
            "public_key":
            "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCTIxtRyT5CuOD74r7UCT+AKzWNxv
            aAP9myjAqR7+vBnJKEvoPnmbKTnm6uLlxutnMbjKrnCCWnQ9vtBVnnd+ElhwLDPADfM
            cJoOqwi7mTcxucckeEbBsfsgYRfdacxgSZL8hVD1hLViQr3xwjEIkJcx1w3x8npvwMu
            TY0uW8+PjwIDAQAB",
            "cipher": "RSA",
            "digest": "SHA224",
            "created": "2018-01-18T10:16:12.364Z",
            "enabled": false
        }
        ```
        The response body of a successful POST request to the ```create
        signature key``` endpoint will contain six properties:
        - ```key_id``` will be a 36 character UUID which can be used to
        enable, delete or get the details.
        - ```public_key``` is used to decrypt the signature.
        - ```cipher``` same as cipher in request body.
        - ```digest``` same as digest in request body.
        - ```created``` is the created date.
        - ```enabled``` is false for the new signature key. You can use the
        ```enable signature key``` endpoint to set this field to true.

        Args:
            body (CreateSignatureKeyRequest): TODO: type description here.
                Example: 

        Returns:
            CreateSignatureKeyResponse: Response from the API. The new
                signature key has been created.

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_signature_key called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_signature_key.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/iam/signature_keys'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_signature_key.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_signature_key.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'create_signature_key')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_signature_key.')
            if _context.response.status_code == 400:
                raise CreateSignatureKey400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CreateSignatureKeyResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
