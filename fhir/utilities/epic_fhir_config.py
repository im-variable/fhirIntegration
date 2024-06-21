import os
import json
import requests
from datetime import datetime, timedelta, timezone
import jwt
import secrets

def generate_random_jti(length=16):
    # Generate a random hex string with the specified length
    jti =  secrets.token_hex(length)
    return jti

def get_bearer_token():
    EPIC_ENDPOINT = os.getenv('EPIC_ENDPOINT')
    try:
        client_id = os.getenv("CLIENT_ID")

        message = {
            'iss': client_id,
            'sub': client_id,
            'aud':  EPIC_ENDPOINT + "/oauth2/token",
            'jti': generate_random_jti(),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'exp': int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        }

        private_key = os.getenv("FHIR_PVT_FILE").replace("\\n", "\n")

        compact_jws = jwt.encode(message, private_key, algorithm='RS384')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': compact_jws
        }
        
        response = requests.post(EPIC_ENDPOINT + "/oauth2/token", headers=headers, data=data)
        response_data = json.loads(response.text)

        bearer_token = response_data['access_token']

        return bearer_token
    except KeyError as e:
        raise e
    except Exception as e:
        raise e

def get_api_headers():
    try:
        bearer_token = get_bearer_token()

        return {
            'Authorization': f"Bearer {bearer_token}",
            'Accept': 'application/fhir+json'
        }
    except KeyError as e:
        raise e
    except Exception as e:
        raise e
