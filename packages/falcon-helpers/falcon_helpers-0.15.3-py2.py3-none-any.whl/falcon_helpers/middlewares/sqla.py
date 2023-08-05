from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

import falcon_helpers.sqla.db as db


class SQLAlchemySessionMiddleware:
    def __init__(self, session):
        # self.session = session
        pass

    def process_resource(self, req, resp, resource, params):
        resource.session = db.session

    def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resource, 'session'):
            return

        try:
            if not req_succeeded:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception as e:
            db.session.remove()
            raise
