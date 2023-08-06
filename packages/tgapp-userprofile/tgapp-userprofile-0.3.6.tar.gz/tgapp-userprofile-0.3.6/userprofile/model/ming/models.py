from ming import schema as s
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass
from datetime import datetime

from userprofile.model import DBSession, provider
from tgext.pluggable import app_model
from tg import url
from tg.decorators import cached_property
from tgext.pluggable.utils import mount_point


class ProfileActivation(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'userprofile_activation'

    _id = FieldProperty(s.ObjectId)
    activated = FieldProperty(s.DateTime)

    old_email_address = FieldProperty(s.String, required=True)
    email_address = FieldProperty(s.String, required=True)

    activation_code = FieldProperty(s.String, required=True, unique=True)

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
        return cls.query.find({'activated': None, 'activation_code': code}).first()

    def get_user(self):
        return app_model.User.query.find({'email_address': self.old_email_address}).one()
