from tg import url
from tg.decorators import cached_property

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation, deferred

from userprofile.model import DBSession
from tgext.pluggable import app_model, primary_key
from tgext.pluggable.utils import mount_point

from datetime import datetime, timedelta


DeclarativeBase = declarative_base()


class ProfileActivation(DeclarativeBase):
    __tablename__ = 'userprofile_activation'

    _id = Column(Integer, autoincrement=True, primary_key=True)
    activated = Column(DateTime)

    old_email_address = Column(Unicode(255), nullable=False)
    email_address = Column(Unicode(255), nullable=False)

    activation_code = Column(Unicode(255), nullable=False, unique=True)

    @cached_property
    def activation_link(self):
        return url(mount_point('userprofile') + '/activate',
                   params=dict(activation_code=self.activation_code),
                   qualified=True)

    @classmethod
    def generate_activation_code(cls, email):
        from hashlib import sha1
        import hmac
        return hmac.new(email.encode(), str(datetime.now()).encode(), sha1).hexdigest()

    @classmethod
    def by_code(cls, code):
        return DBSession.query(cls).filter_by(activated=None, activation_code=code).first()

    def get_user(self):
        return DBSession.query(app_model.User).filter_by(
            email_address=self.old_email_address).first()
