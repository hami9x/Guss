from requesthandler import RequestHandler

class AdminRequestHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("access_acp")
