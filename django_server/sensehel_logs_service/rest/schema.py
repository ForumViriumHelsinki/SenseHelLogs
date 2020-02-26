import re

from django.utils.text import capfirst, camel_case_to_spaces
from rest_framework.schemas.openapi import AutoSchema


def fix_doc(fn):
    fn.__doc__ = re.sub(r'\n(    )*', '\n', fn.__doc__)
    return fn


def override_example_request(example_request):
    def wrapper(fn):
        fn.example_request = example_request
        return fn
    return wrapper


def expected_response_code(code):
    def wrapper(fn):
        fn.expected_response_code = code
        return fn
    return wrapper


class APISchema(AutoSchema):
    def get_operation(self, *args, **kwargs):
        name = self.view.get_queryset().model.__name__ + ' API'
        return dict(super().get_operation(*args, **kwargs), tags=[name])

    def _get_operation_id(self, path, method):
        return getattr(self.view, 'operation_id',
                       capfirst(camel_case_to_spaces(super()._get_operation_id(path, method))))

    def _get_request_body(self, path, method):
        body = super()._get_request_body(path, method)
        content = body.get('content', None)
        action = getattr(self.view, 'action', '')
        action_method = getattr(self.view, action, None)
        example = getattr(action_method, 'example_request', getattr(self.view, 'example_request', None))
        if not (content and example):
            return body
        for schema in content.values():
            schema['example'] = example
        return body

    def _get_responses(self, path, method):
        responses = super()._get_responses(path, method)
        content = responses.get('200', {}).get('content', None)
        action = getattr(self.view, 'action', '')
        action_method = getattr(self.view, action, self.view)

        example = ((action and getattr(self.view, 'example_responses', {}).get(action)) or
                   getattr(self.view, 'example_response', None))

        if content and example:
            for schema in content.values():
                if isinstance(schema, dict):
                    schema['example'] = example

        expected_response_code = getattr(action_method, 'expected_response_code', ((action == 'create') and '201'))

        if responses.get('200', None) and expected_response_code:
            responses[expected_response_code] = responses['200']
            del responses['200']

        return responses
