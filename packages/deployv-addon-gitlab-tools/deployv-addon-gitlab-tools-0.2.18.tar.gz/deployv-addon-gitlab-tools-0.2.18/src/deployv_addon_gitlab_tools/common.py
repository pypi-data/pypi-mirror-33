# coding: utf-8

from os import environ


def check_env_vars(*args, **kwargs):
    missing = []
    not_required = ['psql_image', 'push_image']
    for key in args:
        if key not in not_required and not (key.upper() in environ and environ[key.upper()]):
            missing.append(key.upper())
    for key in kwargs:
        if not (key.upper() in environ and environ[key.upper()]):
            if kwargs[key]:
                environ[key.upper()] = str(kwargs[key])
            elif key not in not_required:
                missing.append(key.upper())
    assert not missing, (
        "Some environment variables were not found: {keys}".format(
            keys=", ".join(missing)
        ))

