from django.contrib.auth import logout

class SingleDeviceLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            if request.user.current_session_key and request.user.current_session_key != current_session_key:
                logout(request)
            else:
                request.user.current_session_key = current_session_key
                request.user.save(update_fields=['current_session_key'])
        
        response = self.get_response(request)
        return response
