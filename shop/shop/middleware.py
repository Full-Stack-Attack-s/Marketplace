class FixIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Берем IP из заголовков Nginx и железобетонно кладем в REMOTE_ADDR
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            request.META['REMOTE_ADDR'] = x_forwarded_for.split(',')[0].strip()
        elif request.META.get('HTTP_X_REAL_IP'):
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
        else:
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            
        return self.get_response(request)
