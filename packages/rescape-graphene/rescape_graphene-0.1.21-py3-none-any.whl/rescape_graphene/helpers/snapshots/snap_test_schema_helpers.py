# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['SchemaHelpersTypeCase::test_create_fields 1'] = [
    'username',
    'password',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active'
]

snapshots['SchemaHelpersTypeCase::test_create_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data',
    'user'
]

snapshots['SchemaHelpersTypeCase::test_merge_with_django_properties 1'] = {
    'date_joined': {
        'create': 'deny',
        'django_type': None,
        'type': 'DateTime',
        'unique': [
        ],
        'update': 'deny'
    },
    'email': {
        'create': [
            'require'
        ],
        'django_type': None,
        'type': 'String',
        'unique': [
        ]
    },
    'first_name': {
        'create': 'require',
        'django_type': None,
        'type': 'String',
        'unique': [
        ]
    },
    'id': {
        'create': 'deny',
        'django_type': None,
        'type': 'Int',
        'unique': [
            'primary',
            'unique',
            'primary',
            'unique',
            'primary',
            'unique'
        ],
        'update': [
            'require'
        ]
    },
    'is_active': {
        'django_type': None,
        'type': 'Boolean',
        'unique': [
        ]
    },
    'is_staff': {
        'django_type': None,
        'type': 'Boolean',
        'unique': [
        ]
    },
    'is_superuser': {
        'django_type': None,
        'type': 'Boolean',
        'unique': [
        ]
    },
    'last_name': {
        'create': 'require',
        'django_type': None,
        'type': 'String',
        'unique': [
        ]
    },
    'password': {
        'create': [
            'require'
        ],
        'django_type': None,
        'read': 'deny',
        'type': 'String',
        'unique': [
        ]
    },
    'username': {
        'create': [
            'require'
        ],
        'django_type': None,
        'type': 'String',
        'unique': [
            'unique',
            'unique',
            'unique'
        ]
    }
}

snapshots['SchemaHelpersTypeCase::test_merge_with_django_properties 2'] = {
    'created_at': {
        'django_type': None,
        'type': 'DateTime',
        'unique': [
        ]
    },
    'data': {
        'default': GenericRepr("'<function <lambda> at 0x100000000>'"),
        'django_type': None,
        'fields': {
            'example': {
                'type': GenericRepr(""<Float meta=<ScalarOptions name='Float'>>"")
            }
        },
        'graphene_type': GenericRepr(""<FooDataType meta=<ObjectTypeOptions name='FooDataType'>>""),
        'type': 'related_input_field_for_crud_type',
        'unique': [
        ]
    },
    'key': {
        'create': 'require',
        'django_type': None,
        'type': 'String',
        'unique': [
            'unique'
        ]
    },
    'name': {
        'create': 'require',
        'django_type': None,
        'type': 'String',
        'unique': [
        ]
    },
    'updated_at': {
        'django_type': None,
        'type': 'DateTime',
        'unique': [
        ]
    },
    'user': {
        'django_type': GenericRepr(""<class 'django.contrib.auth.models.User'>""),
        'fields': {
            'date_joined': {
                'create': 'deny',
                'django_type': None,
                'type': GenericRepr(""<DateTime meta=<ScalarOptions name='DateTime'>>""),
                'unique': [
                ],
                'update': 'deny'
            },
            'email': {
                'create': [
                    'require'
                ],
                'django_type': None,
                'type': GenericRepr(""<String meta=<ScalarOptions name='String'>>""),
                'unique': [
                ]
            },
            'first_name': {
                'create': 'require',
                'django_type': None,
                'type': GenericRepr(""<String meta=<ScalarOptions name='String'>>""),
                'unique': [
                ]
            },
            'id': {
                'create': 'deny',
                'django_type': None,
                'type': GenericRepr(""<Int meta=<ScalarOptions name='Int'>>""),
                'unique': [
                    'primary',
                    'unique',
                    'primary',
                    'unique',
                    'primary',
                    'unique'
                ],
                'update': [
                    'require'
                ]
            },
            'is_active': {
                'django_type': None,
                'type': GenericRepr(""<Boolean meta=<ScalarOptions name='Boolean'>>""),
                'unique': [
                ]
            },
            'is_staff': {
                'django_type': None,
                'type': GenericRepr(""<Boolean meta=<ScalarOptions name='Boolean'>>""),
                'unique': [
                ]
            },
            'is_superuser': {
                'django_type': None,
                'type': GenericRepr(""<Boolean meta=<ScalarOptions name='Boolean'>>""),
                'unique': [
                ]
            },
            'last_name': {
                'create': 'require',
                'django_type': None,
                'type': GenericRepr(""<String meta=<ScalarOptions name='String'>>""),
                'unique': [
                ]
            },
            'password': {
                'create': [
                    'require'
                ],
                'django_type': None,
                'read': 'deny',
                'type': GenericRepr(""<String meta=<ScalarOptions name='String'>>""),
                'unique': [
                ]
            },
            'username': {
                'create': [
                    'require'
                ],
                'django_type': None,
                'type': GenericRepr(""<String meta=<ScalarOptions name='String'>>""),
                'unique': [
                    'unique',
                    'unique',
                    'unique'
                ]
            }
        },
        'graphene_type': GenericRepr(""<UserType meta=<DjangoObjectTypeOptions name='UserType'>>""),
        'type': 'related_input_field_for_crud_type',
        'unique': [
        ]
    }
}

snapshots['SchemaHelpersTypeCase::test_query_fields 1'] = [
    'id',
    'username',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active',
    'date_joined'
]

snapshots['SchemaHelpersTypeCase::test_query_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data'
]

snapshots['SchemaHelpersTypeCase::test_update_fields 1'] = [
    'id',
    'username',
    'password',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active'
]

snapshots['SchemaHelpersTypeCase::test_update_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data',
    'user'
]

snapshots['SchemaHelpersTypeCase::test_update_fields_for_create_or_update 1'] = {
    'defaults': {
        'email': 'dino@barn.farm',
        'first_name': 'T',
        'last_name': 'Rex',
        'password': 'pbkdf2_sha256$100000$not_random$kd71bQn3ng/uGJ/MfuNbDORGyd6XCsWpTCdFOtr+5F0='
    },
    'username': 'dino'
}

snapshots['SchemaHelpersTypeCase::test_update_fields_for_create_or_update 2'] = {
    'defaults': {
        'data': {
            'example': 2.2
        },
        'key': 'fooKey',
        'name': 'Foo Name',
        'user': GenericRepr("<User: dino>")
    }
}
