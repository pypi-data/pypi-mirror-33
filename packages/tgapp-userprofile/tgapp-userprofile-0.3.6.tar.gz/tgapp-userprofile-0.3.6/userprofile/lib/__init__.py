# -*- coding: utf-8 -*-
from hashlib import md5
import tg
from tg import url, request, config
from tgext.pluggable import app_model, plug_url
from tg.i18n import ugettext as _, lazy_ugettext as l_

from tw2.core import Required, MatchValidator
from tw2.forms import ListForm, TextField, TextArea, HiddenField,\
    FileField, SubmitButton, PasswordField, FileValidator

from tgext.mailer import Message as message
from tgext.mailer import get_mailer


def send_email(to_addr, sender, subject, body, rich=None):
    mailer = get_mailer(request)
    message_to_send = message(
        subject=subject,
        sender=sender,
        recipients=[to_addr],
        body=body,
        html=rich or None,
    )
    if config.get('tm.enabled', False):
        mailer.send(message_to_send)
    else:
        mailer.send_immediately(message_to_send)


def get_profile_css(config):
    return url(config['_pluggable_userprofile_config'].get(
        'custom_css', '/_pluggable/userprofile/css/style.css'))


def _get_user_gravatar(email_address):
    if not isinstance(email_address, bytes):
        email_address = email_address.encode('utf-8')
    mhash = md5(email_address).hexdigest()
    return url('http://www.gravatar.com/avatar/'+mhash, params=dict(s=32))


def get_user_data(user):
    user_data = get_profile_data(user, {
        'display_name': (l_('Display Name'), user.display_name),
        'email_address': (l_('Email Address'), user.email_address),
    })

    user_avatar = user_data.pop('avatar', [None, None])[1]

    if user_avatar is None:
        fbauth_info = getattr(user, 'fbauth', None)
        if fbauth_info is not None:
            user_avatar = fbauth_info.profile_picture + '?type=large'
        else:
            user_avatar = _get_user_gravatar(user_data['email_address'][1])

    return user_data, user_avatar


def get_profile_data(user, default):
    # user is not iterable in sqlalchemy
    try:
        return user.profile_data
    except AttributeError:
        return default


def update_user_data(user, user_data):
    for k, v in user_data.items():
        setattr(user, k, v)


class ImageField(FileField):
    inline_engine_name = 'kajiki'
    accept = 'image/*'  # browsers sometimes doesn't support fine control on accept attribute
    accepted_mimetypes = 'image/png, image/jpeg, image/jpg'
    not_accepted_message = l_(' is not accepted (accepted: ')
    template = '''
    <div py:strip="True">
        <script>
            function filefieldPreview(event, id) {
                var output = document.getElementById(id);
                if ('${w.accepted_mimetypes}'.indexOf(event.target.files[0].type) !== -1) {
                    output.style.backgroundImage =
                        "url('" + URL.createObjectURL(event.target.files[0]) + "')";
                } else {
                    alert(event.target.files[0].type +
                        '${w.not_accepted_message}' + '${w.accepted_mimetypes})');
                    event.preventDefault();  // so the input file is not changed
                }
            }
        </script>
        <div id="${w.attrs['id']}-imagefield">
            <div id="${w.attrs['id']}-image" class="userprofile-imagefield-image"
                 style="background-image:url('${w.initial_src}');">
                <label for="${w.attrs['id']}">
                    <span class="glyphicon glyphicon-pencil" aria-hidden="true"> </span>
                     <span id="${w.attrs['id']}-edit-text"> &nbsp; Edit</span>
                </label>
            </div>
            <input style="display: none;" py:attrs="w.attrs"
                   onchange="filefieldPreview(event, '${w.attrs['id']}-image')"
                   accept="${w.accept}"/>
       </div>
    </div>
    '''


class ImageValidator(FileValidator):
    extension = ('png', 'jpeg', 'jpg')
    msgs = {
        'required': ('file_required', l_('Select an image')),
        'badext': l_('File type not accepted. accepted: $extension'),
    }


password_not_prefilled = {
    'autocomplete': 'new-password',  # currentely works only with chrome
    'readonly': '',
    'onfocus': """if (this.hasAttribute('readonly')) {
        this.removeAttribute('readonly');
    }"""
}


class UserForm(ListForm):
    nothing = HiddenField()  # just to create children
    submit = SubmitButton(value=l_('Save'))


def create_user_form(user):
    profile_form = getattr(user, 'profile_form', None)
    if not profile_form:
        user_data, user_avatar = get_user_data(user)
        profile_form = UserForm()
        profile_form.child = profile_form.child()

        profile_form.child.children.append(
            ImageField(id='avatar', name="avatar", initial_src=user_avatar))

        for name, info in user_data.items():
            profile_form.child.children.append(
                TextField(id=name, validator=Required, label=info[0]))

        profile_form = profile_form()
    return profile_form
