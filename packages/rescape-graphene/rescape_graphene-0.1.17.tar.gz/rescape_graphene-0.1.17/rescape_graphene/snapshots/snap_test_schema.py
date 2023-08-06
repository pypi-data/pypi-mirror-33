# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GenaralTypeCase::test_create 1'] = {
    'email': '',
    'firstName': 'T',
    'id': '3',
    'isActive': True,
    'isStaff': False,
    'isSuperuser': False,
    'lastName': 'Rex',
    'password': 'pbkdf2_sha256$36000$not_random$R32ZNyIVxuejYsgH/yYCtx33/GcxrtLcQaV/0u3v0SU=',
    'username': 'dino'
}

snapshots['GenaralTypeCase::test_update 1'] = {
    'email': '',
    'firstName': 'Al',
    'id': '3',
    'isActive': True,
    'isStaff': False,
    'isSuperuser': False,
    'lastName': 'Lissaurus',
    'password': 'pbkdf2_sha256$36000$not_random$R32ZNyIVxuejYsgH/yYCtx33/GcxrtLcQaV/0u3v0SU=',
    'username': 'dino'
}

snapshots['GenaralTypeCase::test_query 1'] = [
    {
        'email': '',
        'firstName': 'Simba',
        'id': '1',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'The Lion',
        'password': 'pbkdf2_sha256$36000$not_random$LENtt0mm42KokrFiuj5Wj3UrX/+ebFmeGe0Q204HT7M=',
        'username': 'lion'
    },
    {
        'email': '',
        'firstName': 'Felix',
        'id': '2',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'The Cat',
        'password': 'pbkdf2_sha256$36000$not_random$i7vhgi5Pl/0XuVY32+EW2fTMNyLAP6p4iR7j54hYIQ8=',
        'username': 'cat'
    },
    {
        'email': '',
        'firstName': 'T',
        'id': '3',
        'isActive': True,
        'isStaff': False,
        'isSuperuser': False,
        'lastName': 'Rex',
        'password': 'pbkdf2_sha256$36000$not_random$R32ZNyIVxuejYsgH/yYCtx33/GcxrtLcQaV/0u3v0SU=',
        'username': 'dino'
    }
]
