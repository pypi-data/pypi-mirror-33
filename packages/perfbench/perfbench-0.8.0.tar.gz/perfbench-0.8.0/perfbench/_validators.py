#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import types
import cerberus


class ValidationError(Exception):
    pass


def create_dataset_validator():
    '''Create a validator for a dataset.'''
    class validator(cerberus.Validator):
        def _validate_type_stmt(self, value):
            return isinstance(value, types.FunctionType)

    schema = dict(
        stmt=dict(
            type='stmt',
            required=True
        ),
        title=dict(
            type='string',
            required=False,
            empty=True
        )
    )

    return validator(schema)


def validate_datasets(datasets):
    '''Validate datasets.'''
    errors = []
    v = create_dataset_validator()
    for i, dataset in enumerate(datasets):
        if not v.validate(dataset):
            errors.append('{}: {}'.format(i, v.errors))
    if errors:
        raise ValidationError('datasets\n' + '\n'.join(errors))


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


def create_kernel_validator():
    '''Create a validator for a kernel.'''
    class validator(cerberus.Validator):
        def _validate_type_stmt(self, value):
            return isinstance(value, types.FunctionType)

    schema = dict(
        stmt=dict(
            type='stmt',
            required=True
        ),
        label=dict(
            type='string',
            required=False,
            empty=True
        )
    )

    return validator(schema)


def validate_kernels(kernels):
    '''Validate kernels.'''
    errors = []
    v = create_kernel_validator()
    for i, kernel in enumerate(kernels):
        if not v.validate(kernel):
            errors.append('{}: {}'.format(i, v.errors))
    if errors:
        raise ValidationError('kernels\n' + '\n'.join(errors))


def create_layout_size_validator():
    '''Create a validator for a layout size.'''
    schema = dict(
        label=dict(
            type='string',
            required=False,
            empty=True
        ),
        width=dict(
            type='integer',
            required=False,
            min=0
        ),
        height=dict(
            type='integer',
            required=False,
            min=0
        ),
    )

    return cerberus.Validator(schema)


def validate_layout_sizes(layout_sizes):
    '''Validate layout sizes.'''
    errors = []
    v = create_layout_size_validator()
    for i, layout_size in enumerate(layout_sizes):
        if not v.validate(layout_size):
            errors.append('{}: {}'.format(i, v.errors))
    if errors:
        raise ValidationError('layout_sizes\n' + '\n'.join(errors))
