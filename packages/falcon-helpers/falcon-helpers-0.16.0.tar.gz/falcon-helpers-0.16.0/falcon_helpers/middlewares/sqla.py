import falcon_helpers.sqla.db as db


class SQLAlchemySessionMiddleware:
    def __init__(self, session=None):
        self.session = session or db.session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.session

    def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resource, 'session'):
            return

        try:
            if not req_succeeded:
                self.session.rollback()
            else:
                self.session.commit()

        except Exception as e:
            self.session.remove()
            raise
