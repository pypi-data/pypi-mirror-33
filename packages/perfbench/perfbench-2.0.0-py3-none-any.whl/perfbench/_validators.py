#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cerberus


class ValidationError(Exception):
    pass


def create_dataset_sizes_validator():
    '''Create a validator for dataset sizes.'''
    schema = dict(
        a_list=dict(
            type='list',
            schema=dict(
                type='integer',
                min=1
            )
        )
    )

    return cerberus.Validator(schema)


def validate_dataset_sizes(dataset_sizes):
    '''Validate dataset sizes.'''
    v = create_dataset_sizes_validator()
    if not v.validate(dict(a_list=dataset_sizes)):
        raise ValidationError('dataset_sizes ' + str(v.errors))
