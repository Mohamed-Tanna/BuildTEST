class IgnoreTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization')

        if token:
            request.META['IGNORE_TOKEN'] = True

        response = self.get_response(request)

        return response
