def get_request_class():
    from .request import AdharaRequest
    return AdharaRequest


def get_response_class():
    from .response import AdharaResponse
    return AdharaResponse


def get_rest_view_class():
    from .restview import RestView
    return RestView
