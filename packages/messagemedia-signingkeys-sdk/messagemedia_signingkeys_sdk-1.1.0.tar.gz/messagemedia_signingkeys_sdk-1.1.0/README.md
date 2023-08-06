# MessageMedia Signature Key Management Python SDK
[![Travis Build Status](https://api.travis-ci.org/messagemedia/signingkeys-python-sdk.svg?branch=master)](https://travis-ci.org/messagemedia/signingkeys-python-sdk)
[![PyPI version](https://badge.fury.io/py/messagemedia-signingkeys-sdk.svg)](https://badge.fury.io/py/messagemedia-signingkeys-sdk)

The MessageMedia Signature Key API provides a number of endpoints for managing key used to sign each unique request to ensure security and the requests can't (easily) be spoofed. This is similar to using HMAC in your outbound messaging (rather than HTTP Basic).

## ⭐️ Install via PIP
Run the following command to install the SDK via pip:
`pip install messagemedia-signingkeys-sdk`

## 🎬 Get Started
It's easy to get started. Simply enter the API Key and secret you obtained from the [MessageMedia Developers Portal](https://developers.messagemedia.com) into the code snippet below.

### 🚀 Create a signature key
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

body_value = "{   \"digest\": \"SHA224\",   \"cipher\": \"RSA\" }"
body = json.loads(body_value)

result = signature_key_management_controller.create_signature_key(body)

```

### 📥 Get signature key details
You can get a key_id by looking at the id of the signature key created from the response of the above example.
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

key_id = 'key_id'

result = signature_key_management_controller.get_signature_key_detail(key_id)

```

### 📥 Get signature keys list
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

result = signature_key_management_controller.get_signature_key_list()

```

### ❌ Delete signature key
You can get the key_id by looking at the ids of the signature keys returned from the response of the `Get signature keys list` example.
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

key_id = 'key_id'

signature_key_management_controller.delete_signature_key(key_id)

```

### ☑️ Enable a signature key
You can get the key_id by looking at the ids of the signature keys returned from the response of the `Get signature keys list` example.
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

body = EnableSignatureKeyRequest({
  "key_id": "7ca628a8-08b0-4e42-aeb8-960b37049c31"
})

result = signature_key_management_controller.update_enable_signature_key(body)

```

### 📥 Get enabled signature key
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

result = signature_key_management_controller.get_enabled_signature_key()

```

### 🚫 Disable an enabled signature key
```python
from message_media_signing_keys.message_media_signing_keys_client import MessageMediaSigningKeysClient

# Configuration parameters and credentials
basic_auth_user_name = 'basic_auth_user_name' # The username to use with basic authentication
basic_auth_password = 'basic_auth_password' # The password to use with basic authentication

client = MessageMediaSigningKeysClient(basic_auth_user_name, basic_auth_password)

signature_key_management_controller = client.signature_key_management

signature_key_management_controller.delete_disable_the_current_enabled_signature_key()

```

## 📕 Documentation
Check out the [full API documentation](DOCUMENTATION.md) for more detailed information.

## 😕 Need help?
Please contact developer support at developers@messagemedia.com or check out the developer portal at [developers.messagemedia.com](https://developers.messagemedia.com/)

## 📃 License
Apache License. See the [LICENSE](LICENSE) file.
