from .base import configure_app, create_app, flush_db_changes
from tgext.pluggable import app_model
from userprofile import model


class UserProfileControllerTests(object):

    def setup(self):
        self.app = create_app(self.app_config, False)
        self.env = {'REMOTE_USER': 'pippo'}

        user = app_model.User()
        user.user_name = 'pippo'
        user.display_name = 'Pippo Plutonico'
        user.email_address = 'pippo@tg.2'
        user.password = 'bella'
        flush_db_changes(add_all=[user])

    def test_app_index(self):
        # needed to know that the application starts without errors with this pluggable
        r = self.app.get('/')
        assert 'HELLO' in r.text

    def test_index_anon(self):
        # if you're not logged in you should get a 401
        self.app.get('/userprofile', status=401)

    def test_index(self):
        r = self.app.get('/userprofile', extra_environ=self.env, status=200)
        assert 'Pippo Plutonico' in r.text, r.text

    def test_edit(self):
        r = self.app.get('/userprofile/edit', extra_environ=self.env, status=200)
        assert 'Pippo Plutonico' == r.pyquery('input[name="display_name"]').val()

    def test_save(self):
        r = self.app.get(
            '/userprofile/save',
            params={
                'nothing': '',
                'display_name': 'Pippo Topoloso',
                'email_address': 'pippo@tg.2',  # same email
            },
            extra_environ={'REMOTE_USER': 'pippo'},
            status=302,
        )
        assert r.follow(status=200, extra_environ=self.env)
        u = app_model.User.by_user_name('pippo')
        assert u.display_name == 'Pippo Topoloso'
        assert u.user_name == 'pippo'
        assert u.email_address == 'pippo@tg.2'

    def test_save_fail_so_test_validation(self):
        r = self.app.get(
            '/userprofile/save',
            params={
                'nothing': '',
                'display_name': '',
                'email_address': 'pippo@tg.2'
            },
            extra_environ={'REMOTE_USER': 'pippo'},
            status=200,
        )
        assert r.pyquery('input[name="display_name"]').val() == ''
        assert 'id="display_name:error"' in r.text

    def test_change_email(self):
        self.app.get(
            '/userprofile/save',
            params={
                'nothing': '',
                'email_address': 'pi@tg.2',
                'display_name': 'Pi PPO'
            },
            extra_environ={'REMOTE_USER': 'pippo'},
            status=302,
        )
        act = model.provider.query(model.ProfileActivation)[1][0]
        assert act.old_email_address == 'pippo@tg.2'
        assert act.email_address == 'pi@tg.2'
        assert not act.activated
        assert act.activation_code

        self.app.get(
            '/userprofile/activate',
            params={
                'activation_code': act.activation_code,
            },
            status=302,
        )

        act = model.provider.query(model.ProfileActivation)[1][0]
        assert act.activated
        u = app_model.User.by_user_name('pippo')
        assert u.display_name == 'Pi PPO'


class TestUserProfileControllerSQLA(UserProfileControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestUserProfileControllerMing(UserProfileControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')
