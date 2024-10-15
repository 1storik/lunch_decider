class CheckAppVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        app_version = request.headers.get('X-App-Version')
        if app_version:
            request.app_version = app_version
        else:
            request.app_version = '1.0'

        response = self.get_response(request)
        return response
