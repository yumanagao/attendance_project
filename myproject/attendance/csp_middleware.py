class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # 安全なCSP: ローカルJSのみ許可
        response['Content-Security-Policy'] = "script-src 'self'"
        return response