# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['SchemaHelpersTypeCase::test_create_fields 1'] = GenericRepr("dict_keys(['username', 'password', 'email', 'is_superuser', 'first_name', 'last_name', 'is_staff', 'is_active'])")

snapshots['SchemaHelpersTypeCase::test_merge_with_django_properties 1'] = {
    'date_joined': {
        'create': 'deny',
        'type': 'DateTime',
        'unique': [
        ],
        'update': 'deny'
    },
    'email': {
        'create': [
            'require'
        ],
        'type': 'String',
        'unique': [
        ]
    },
    'first_name': {
        'create': 'require',
        'type': 'String',
        'unique': [
        ]
    },
    'id': {
        'create': 'deny',
        'type': 'Int',
        'unique': [
            'primary',
            'unique'
        ],
        'update': [
            'require'
        ]
    },
    'is_active': {
        'type': 'Boolean',
        'unique': [
        ]
    },
    'is_staff': {
        'type': 'Boolean',
        'unique': [
        ]
    },
    'is_superuser': {
        'type': 'Boolean',
        'unique': [
        ]
    },
    'last_name': {
        'create': 'require',
        'type': 'String',
        'unique': [
        ]
    },
    'password': {
        'create': [
            'require'
        ],
        'read': 'deny',
        'type': 'String',
        'unique': [
        ]
    },
    'username': {
        'create': [
            'require'
        ],
        'type': 'String',
        'unique': [
            'unique'
        ]
    }
}

snapshots['SchemaHelpersTypeCase::test_query_fields 1'] = GenericRepr("dict_keys(['id', 'username', 'email', 'is_superuser', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined'])")

snapshots['SchemaHelpersTypeCase::test_update_fields 1'] = GenericRepr("dict_keys(['id', 'username', 'password', 'email', 'is_superuser', 'first_name', 'last_name', 'is_staff', 'is_active'])")

snapshots['SchemaHelpersTypeCase::test_update_fields_for_create_or_update 1'] = {
    'defaults': {
        'email': 'dino@barn.farm',
        'first_name': 'T',
        'last_name': 'Rex',
        'password': 'pbkdf2_sha256$100000$not_random$kd71bQn3ng/uGJ/MfuNbDORGyd6XCsWpTCdFOtr+5F0='
    },
    'username': 'dino'
}
