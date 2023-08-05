# Apex NG Authentication

This package contains python methods to simplify communication with the Apex NG backend.

## Usage

$ pip install apex_auth

When the package is installed you can then create signatures by using the ApexRequest.create_request_headers method.
The returned value will be usable for sending to the backend and should authenticate correctly.
