from typing import Optional, Union
from datetime import datetime
import hashlib
import json

from base64 import b64encode, b64decode

from django.http.request import HttpRequest
from rest_framework.request import Request


class ApexRequest:
    @staticmethod
    def create_request_headers(public_key: str, private_key: str, data: Optional[dict]) -> dict:
        timestamp = datetime.utcnow().isoformat()

        encoded_body = hashlib.sha256((json.dumps(data) if data else "").encode()).digest()

        signature = hashlib.sha256((public_key +
                                    str(encoded_body) +
                                    timestamp +
                                    private_key).encode()).digest()
        return {
            "Signature": b64encode(signature).decode(),
            "Timestamp": timestamp,
            "API-Token": b64encode(public_key.encode()).decode()
        }

    @staticmethod
    def get_validation_headers(request: Union[HttpRequest, Request]) -> dict:
        if isinstance(request, HttpRequest):
            public_key_header = request.META.get("API-Token")
            public_key = b64decode(public_key_header.decode())
            return {
                "Public-Key": public_key,
                "Timestamp": request.META.get("Timestamp"),
                "Signature": request.META.get("Signature")
            }
        else:
            public_key_header = request.META.get("HTTP_API_TOKEN")
            public_key = b64decode(public_key_header.decode())
            return {
                "Public-Key": public_key,
                "Timestamp": request.META.get("HTTP_TIMESTAMP"),
                "Signature": request.META.get("HTTP_SIGNATURE")
            }

    @staticmethod
    def signature_is_valid(request: HttpRequest, public_key: str, private_key: str, timestamp: str,
                           actual_signature: str) -> bool:
        if request.method == "GET":
            encoded_body = hashlib.sha256(b"").digest()
        else:
            encoded_body = hashlib.sha256(json.dumps(request.POST).encode()).digest()

        signature = hashlib.sha256(
            (public_key +
             str(encoded_body) +
             timestamp +
             private_key).encode()).digest()

        return actual_signature == b64encode(signature).decode()
