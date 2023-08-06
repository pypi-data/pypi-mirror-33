from python_ottawa_transit.api import OCTransportApi
from flask import current_app, _app_ctx_stack


class OCTransport(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def connect(self):
        return OCTransportApi(
            current_app.config["OTTAWA_TRANSIT_APP_ID"],
            current_app.config["OTTAWA_TRANSIT_API_KEY"],
        )

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        pass

    @property
    def api(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "ot_api"):
                ctx.ot_api = self.connect()
            return ctx.ot_api
