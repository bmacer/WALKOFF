import logging

import pytest
from flask.testing import FlaskClient
import yaml

from testing.api_gateway.helpers import assert_crud_resource

logger = logging.getLogger(__name__)
apps_url = "/api/apps"
apps_api_url = "/api/apps/apis"


# TOP LEVEL APP API TESTS


def test_sanity_check(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that Execution Database is empty"""

    p = api_gateway.get(apps_url, headers=auth_header)
    assert p.get_json() == []


# def test_create_api_empty(api_gateway: FlaskClient, auth_header, execdb):
#     """Assert that an API without actions is rejected"""
#
#     inputs = [
#         {
#             "create": """
#             walkoff_version: 1.0.0
#             app_version: 1.0.0
#             name: test_app:1.0.0
#             description: An invalid App API with missing actions
#             """
#         }
#     ]
#     assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load, valid=False)


def test_create_api_minimum(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that a minimum valid API is accepted"""

    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            description: A minimum valid App API
            actions:
              - name: test_action
            """
        }
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load)


def test_create_api_invalid_semver(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that walkoff_version, app_version, name all have correct sematic versioning"""

    inputs = [
        {
            "create": """
            walkoff_version: "1.0"
            app_version: 1.0.0
            name: test_app:1.0.0
            description: An invalid App API with bad semantic versioning in walkoff_version
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: "1.0"
            name: test_app2:1.0.0
            description: An invalid App API with bad semantic versioning in app_version
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app3:1.0
            description: An invalid App API with bad semantic versioning in name
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app4:1.0.1
            description: An invalid App API with mismatched semantic versioning in name and app_version
            actions:
              - name: test_action
            """
        }
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load, valid=False)


def test_create_api_valid_contact(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that valid contact info is accepted"""

    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            contact_info:
              name: name
              url: example.com
              email: example@example.com
            description: An invalid App API with non-object contact info
            actions:
              - name: test_action
            """,
        },
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load)


def test_create_api_invalid_contact(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that various invalid contact info are rejected"""

    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            contact_info: not an object
            description: An invalid App API with non-object contact info
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app2:1.0.0
            contact_info: 
              name: good
              bad: not good
            description: An invalid App API with extra field in contact
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app3:1.0.0
            contact_info: 
              name: name
              email: not a valid email
            description: An invalid App API with invalid email in contact
            actions:
              - name: test_action
            """,
        },
        # URL format from connexion/jsonschema does not seem to actually validate anything
        # """
        #     walkoff_version: 1.0.0
        #     app_version: 1.0.0
        #     name: test_app:1.0.0
        #     contact_info:
        #       name: name
        #       url: http://not a valid url
        #     description: An invalid App API with invalid URL in contact
        #     actions:
        #       - name: test_action
        # """
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load, valid=False)


def test_create_api_invalid_license(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that various invalid license info are rejected"""

    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            license_info: not an object
            description: An invalid App API with non-object license info
            actions:
              - name: test_action
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app2:1.0.0
            license_info: 
              name: good
              bad: not good
            description: An invalid App API with extra field in license
            actions:
              - name: test_action
            """,
        },
        # URL format from connexion/jsonschema does not seem to actually validate anything
        # """
        #     walkoff_version: 1.0.0
        #     app_version: 1.0.0
        #     name: test_app:1.0.0
        #     license_info:
        #       name: name
        #       url: http://not a valid url
        #     description: An invalid App API with invalid URL in license
        #     actions:
        #       - name: test_action
        # """
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load, valid=False)


# TOP LEVEL ACTION TESTS


def test_create_api_valid_parameters(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that valid parameters are accepted"""
    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            description: A valid App API with minimum parameter info
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    schema: 
                      type: string
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app2:1.0.0
            description: A valid App API with all fields and required 
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: 42
                    required: true
                    schema: 
                      type: number
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app3:1.0.0
            description: A valid App API with all fields and required set to false (default)
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    required: false
                    schema: 
                      type: boolean
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app4:1.0.0
            description: A valid App API with object schema
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    required: false
                    schema: 
                      type: object
                      required: [name, id]
                      properties:
                        name:
                          type: string
                        id:
                          type: number
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app5:1.0.0
            description: A valid App API with object schema in multiple params
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    required: false
                    schema: 
                      type: object
                      required: [name, id]
                      properties:
                        name:
                          type: string
                        id:
                          type: number
              - name: test_action2
                parameters: 
                  - name: param2
                    description: A parameter description
                    placeholder: A placeholder
                    required: false
                    schema: 
                      type: object
                      required: [name, id]
                      properties:
                        name:
                          type: string
                        id:
                          type: number
        """,
        },
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load)


def test_create_api_invalid_parameters(api_gateway: FlaskClient, auth_header, execdb):
    """Assert that invalid parameters are rejected"""
    inputs = [
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app:1.0.0
            description: An invalid App API with bad schema type
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    schema: 
                      type: notatype
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app2:1.0.0
            description: An invalid App API with missing parameter name
            actions:
              - name: test_action
                parameters: 
                  - description: A parameter description
                    placeholder: A placeholder
                    schema: 
                      type: notatype
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app3:1.0.0
            description: A valid App API with minimum parameter info
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    schema: 
                      type: object
                      properties:
            """,
        },
        {
            "create": """
            walkoff_version: 1.0.0
            app_version: 1.0.0
            name: test_app4:1.0.0
            description: A valid App API with minimum parameter info
            actions:
              - name: test_action
                parameters: 
                  - name: param1
                    description: A parameter description
                    placeholder: A placeholder
                    schema: 
                      type: notatype
            """,
        },
    ]
    assert_crud_resource(api_gateway, auth_header, apps_api_url, inputs, yaml.full_load, valid=False)
