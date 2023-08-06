import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase
from django.test.utils import override_settings
from generic.repositories import GenericRepository
from generic.validators import validate_many
from rest_framework.test import APIClient
from utility.exceptions import (ValidationError,
                                ObjectNotFoundError,
                                InternalError)
from utility.functions import (str_to_uuid1, get_current_datetime)

from authentication.helper import get_rand_str
from authentication.models import (User, AuthToken)
from authentication.repositories import (TokenRepository,
                                         ResetRepository,
                                         MailVerificationRepository)
from authentication.services import (retrieve_token_service,
                                     logout_service,
                                     logout_all_service,
                                     refresh_token_service,
                                     reset_password_service,
                                     validate_reset_password_service,
                                     confirm_reset_password_service,
                                     validate_email_service,
                                     confirm_email_service)
from authentication.validators import (is_password_length_sufficient,
                                       does_contain_char_classes,
                                       is_email_valid)


class RepositoryTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_delete_by_user(self):
        repo = TokenRepository()

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        num_of_tokens1 = len(list(AuthToken.objects.filter(user=user)))
        repo.delete_by_user(user)
        num_of_tokens2 = len(list(AuthToken.objects.filter(user=user)))
        self.assertEqual(num_of_tokens1 - 1, num_of_tokens2)

    def test_create_token(self):
        repo = TokenRepository()

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        for i in range(0, 9):
            num_of_tokens1 = AuthToken.objects.filter(user=user).count()
            repo.create_token(user)
            num_of_tokens2 = AuthToken.objects.filter(user=user).count()
            self.assertEqual(num_of_tokens1 + 1, num_of_tokens2)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        repo.create_token(user)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_delete_expired_tokens(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        token = list(AuthToken.objects.filter(user=user))[0]
        token.created = (get_current_datetime()
                         - settings.REFRESH_TOKEN_EXPIRY
                         - timedelta(hours=1))
        token.save()
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(1, num_of_tokens)

        repo.delete_expired_tokens(settings.REFRESH_TOKEN_EXPIRY)
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(0, num_of_tokens)

    def test_logout(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        num_of_tokens1 = AuthToken.objects.filter(user=user).count()

        (key, r_key) = repo.create_token(user)

        key2 = 'Z{0}'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.logout(key2)

        key3 = '{0}Z'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.logout(key3)

        repo.logout(key)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_logout_all(self):
        repo = TokenRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        (key, r_key) = repo.create_token(user)
        num_of_tokens1 = AuthToken.objects.filter(user=user).count()

        key2 = 'Z{0}'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.refresh_token(user, key2, r_key)

        key3 = '{0}Z'.format(key)
        with self.assertRaises(ObjectNotFoundError):
            repo.refresh_token(user, key3, r_key)

        repo.refresh_token(user, key, r_key)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_reset_password(self):
        repo = ResetRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        with self.assertRaises(ValidationError):
            repo.reset_password(user.email)

        user_id = str_to_uuid1('43c6c78a-7ec2-11e8-a16a-acde48001122')
        user = User.objects.get(id=user_id)

        with self.assertRaises(ValidationError):
            repo.reset_password(user.email)

        with self.assertRaises(ObjectNotFoundError):
            repo.reset_password('i.dont@exist.com')

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)

        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_reset_password_internal_error(self):
        repo = ResetRepository()

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)

        with self.assertRaises(InternalError):
            repo.reset_password(user.email)

    def test_validate_token_and_get_user(self):
        repo = ResetRepository()

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)

        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

        returned_user = repo.validate_token_and_get_user(token)
        self.assertEqual(user, returned_user)

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user('invalidToken')

        token = signing.dumps({'user': str(user.id),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user(token)

        token = signing.dumps({'userId': str(uuid.uuid1()),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')

        with self.assertRaises(ObjectNotFoundError):
            repo.validate_token_and_get_user(token)

    @override_settings(RESET_TOKEN_EXPIRY=timedelta(seconds=0))
    def test_validate_token_and_get_user_timeout(self):
        repo = ResetRepository()

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)

        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user(token)

    def test_send_email_validation(self):
        repo = MailVerificationRepository()
        user_id = str_to_uuid1('7eff0578-6cb7-11e8-a2eb-acde48001122')
        user = User.objects.get(id=user_id)
        with self.assertRaises(ValidationError):
            repo.send_email_validation(user)

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        with self.assertRaises(ValidationError):
            repo.send_email_validation(user)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.send_email_validation(user)
        self.assertEqual(1, result)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_send_email_validation_error(self):
        repo = MailVerificationRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        with self.assertRaises(InternalError):
            repo.send_email_validation(user)

    def test_validate_email_confirmation(self):
        repo = MailVerificationRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.send_email_validation(user)
        self.assertEqual(1, result)

        returned_user = repo.validate_token_and_get_user(token)
        self.assertEqual(user, returned_user)

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user('invalidToken')

        token = signing.dumps({'user': str(user.id),
                               'rand': get_rand_str(16)},
                              salt='verify_email_add')

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user(token)

        token = signing.dumps({'userId': str(uuid.uuid1()),
                               'rand': get_rand_str(16)},
                              salt='verify_email_add')

        with self.assertRaises(ObjectNotFoundError):
            repo.validate_token_and_get_user(token)

    @override_settings(VAL_TOKEN_EXPIRY=timedelta(seconds=0))
    def test_validate_email_confirmation_timeout(self):
        repo = MailVerificationRepository()

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        (result, token) = repo.send_email_validation(user)
        self.assertEqual(1, result)

        with self.assertRaises(ValidationError):
            repo.validate_token_and_get_user(token)


class ValidatorTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_is_password_length_sufficient(self):
        repo = GenericRepository(User)
        validator = is_password_length_sufficient(repo, 12)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1Nice#Pass')
            validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)

    def test_does_contain_char_classes(self):
        repo = GenericRepository(User)
        validator = does_contain_char_classes(repo, 3)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1nicepassword')
            validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)

        with self.assertRaises(ImproperlyConfigured):
            does_contain_char_classes(repo, -1)

        with self.assertRaises(ImproperlyConfigured):
            does_contain_char_classes(repo, 5)

    def test_is_email_valid(self):
        repo = GenericRepository(User)
        validator = is_email_valid(repo)
        user = User(email='john.doe@example.com', password='1Nice#Password')

        result = validator(user)
        self.assertEqual(True, result)

        with self.assertRaises(ValidationError):
            user = User(email='john.doe@example', password='1Nice#Password')
            validator(user)

        users = User.objects.all()
        result = validator(users)
        self.assertEqual(True, result)


class ServiceTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_retrieve_token_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        retrieve(user)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1 + 1, num_of_tokens2)

    def test_logout_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)
        logout = logout_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        (token, refresh_token) = retrieve(user)
        logout(token)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_logout_all_service(self):
        repo = TokenRepository()
        logout = logout_all_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        logout(user)
        num_of_tokens = AuthToken.objects.filter(user=user).count()
        self.assertEqual(0, num_of_tokens)

    def test_refresh_token_service(self):
        repo = TokenRepository()
        retrieve = retrieve_token_service(repo)
        refresh = refresh_token_service(repo)

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (token, refresh_token) = retrieve(user)

        num_of_tokens1 = AuthToken.objects.filter(user=user).count()
        refresh(user, token, refresh_token)
        num_of_tokens2 = AuthToken.objects.filter(user=user).count()
        self.assertEqual(num_of_tokens1, num_of_tokens2)

    def test_reset_password_service(self):
        repo = ResetRepository()
        reset = reset_password_service(repo)

        email = 'test@example.com'
        (result, token) = reset(email)
        self.assertEqual(1, result)

    def test_validate_reset_password_service(self):
        repo = ResetRepository()
        test = validate_reset_password_service(repo)

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

        returned_user = test(token)
        self.assertEqual(user, returned_user)

    def test_confirm_reset_password_service(self):
        repo = ResetRepository()
        val_repo = GenericRepository(User)
        vs = (is_password_length_sufficient(val_repo,
                                            settings.MIN_PASSWORD_LENGTH),
              does_contain_char_classes(val_repo,
                                        settings.CHAR_CLASSES))
        confirm = confirm_reset_password_service(repo, validate_many(*vs))
        new_password = 'IAm1NewPass#Word'

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

        returned_user = confirm(token, new_password)
        self.assertEqual(user, returned_user)
        self.assertEqual(True, check_password(new_password,
                                              returned_user.password))

    def test_validate_email_service(self):
        repo = MailVerificationRepository()
        val_repo = GenericRepository(User)
        vs = (is_email_valid(val_repo),)
        validate = validate_email_service(repo, validate_many(*vs))

        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)

        (result, token) = validate(user)
        self.assertEqual(1, result)

    def test_confirm_email_service(self):
        repo = MailVerificationRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.send_email_validation(user)
        self.assertEqual(1, result)

        confirm = confirm_email_service(repo)
        returned_user = confirm(token)
        self.assertEqual(returned_user, user)
        self.assertNotEqual(returned_user.validated_email, user.validated_email)


class ViewTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_password_requirements_view(self):
        client = APIClient()
        request = client.get('/password.json', format='json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(settings.MIN_PASSWORD_LENGTH,
                         request.data['minimalLength'])
        self.assertEqual(settings.CHAR_CLASSES, request.data['charClasses'])

    def test_user_view_set(self):
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        client = APIClient()
        client.force_authenticate(user=user)

        request = client.get('/users.json', format='json')
        self.assertEqual(200, request.status_code)

        request = client.get('/users/{0}.json'.format(user_id), format='json')
        self.assertEqual(200, request.status_code)
        self.assertEqual(str(user_id), request.data['id'])

        name = 'New Name'
        request = client.patch('/users/{0}.json'.format(user_id),
                               {'username': user.username, 'firstName': name},
                               format='json')
        self.assertEqual(200, request.status_code)
        request = client.get('/users/{0}.json'.format(user_id), format='json')
        self.assertEqual(name, request.data['firstName'])

        request = client.delete('/users/{0}.json'.format(user_id),
                                format='json')
        self.assertEqual(200, request.status_code)

        request = client.get('/users/{0}.json'.format(user_id), format='json')
        self.assertEqual(404, request.status_code)

    def test_register_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)

        request = client.get('/users/{0}.json'.format(user_id), format='json')
        self.assertEqual(username, request.data['username'])

        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(400, request.status_code)

    def test_token_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)

        request = client.post('/token.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)

        request = client.post('/token.json',
                              {'wrongKey': username, 'password': password},
                              format='json')
        self.assertEqual(400, request.status_code)

    def test_logout_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']
        user = User.objects.get(id=user_id)

        request = client.post('/token.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']

        request = client.get('/logout.json', format='json')
        self.assertEqual(401, request.status_code)

        client.force_authenticate(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        request = client.get('/logout.json', format='json')
        self.assertEqual(204, request.status_code)

        client = APIClient()
        client.force_authenticate(user=user)
        token = token.replace('0', '1')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        request = client.get('/logout.json', format='json')
        self.assertEqual(401, request.status_code)

    def test_logout_all_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']
        user = User.objects.get(id=user_id)

        request = client.post('/token.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']

        request = client.get('/logoutall.json', format='json')
        self.assertEqual(401, request.status_code)

        client.force_authenticate(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        request = client.get('/logoutall.json', format='json')
        self.assertEqual(204, request.status_code)

    def test_refresh_view_set(self):
        client = APIClient()
        username = 'username'
        password = '1#Password'
        request = client.post('/register.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(201, request.status_code)
        user_id = request.data['id']
        user = User.objects.get(id=user_id)

        request = client.post('/token.json',
                              {'username': username, 'password': password},
                              format='json')
        self.assertEqual(200, request.status_code)
        token = request.data['token']
        refresh_token = request.data['refreshToken']

        request = client.post('/refresh.json',
                              {'refreshToken': refresh_token},
                              format='json')
        self.assertEqual(401, request.status_code)

        client.force_authenticate(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/refresh.json',
                              {'username': username},
                              format='json')
        self.assertEqual(400, request.status_code)

        request = client.post('/refresh.json',
                              {'refreshToken': refresh_token},
                              format='json')
        self.assertEqual(200, request.status_code)

        request = client.post('/refresh.json',
                              {'refreshToken': refresh_token.replace('0', '1')},
                              format='json')
        self.assertEqual(401, request.status_code)

    def test_reset_password_view_set(self):
        client = APIClient()
        email = 'test@example.com'
        request = client.post('/resetpassword.json',
                              {'email': email},
                              format='json')
        self.assertEqual(204, request.status_code)

        request = client.post('/resetpassword.json',
                              {'username': email},
                              format='json')
        self.assertEqual(400, request.status_code)

        email = 'idont@exist.com'
        request = client.post('/resetpassword.json',
                              {'email': email},
                              format='json')
        self.assertEqual(404, request.status_code)

        email = 'josef@k.at'
        request = client.post('/resetpassword.json',
                              {'email': email},
                              format='json')
        self.assertEqual(400, request.status_code)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_reset_password_view_set_error(self):
        client = APIClient()
        email = 'test@example.com'
        request = client.post('/resetpassword.json',
                              {'email': email},
                              format='json')
        self.assertEqual(500, request.status_code)

    def test_validate_password_view_set(self):
        repo = ResetRepository()
        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)
        client = APIClient()

        url = "/validatereset/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(204, request.status_code)

        token = signing.dumps({'user': str(user.id),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')
        url = "/validatereset/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(400, request.status_code)

        token = signing.dumps({'userId': str(uuid.uuid1()),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')
        url = "/validatereset/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(404, request.status_code)

    def test_confirm_password_view_set(self):
        repo = ResetRepository()
        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.reset_password(user.email)
        self.assertEqual(1, result)

        new_password = 'NewSecurePassword#123'
        client = APIClient()
        request = client.post('/confirmreset.json',
                              {'resetToken': token,
                               'password': new_password},
                              format='json')
        self.assertEqual(204, request.status_code)

        request = client.post('/token.json',
                              {'username': user.username,
                               'password': new_password},
                              format='json')
        self.assertEqual(200, request.status_code)

        request = client.post('/confirmreset.json',
                              {'resetToken': token},
                              format='json')
        self.assertEqual(400, request.status_code)

        request = client.post('/confirmreset.json',
                              {'password': new_password},
                              format='json')
        self.assertEqual(400, request.status_code)

        token = signing.dumps({'user': str(user.id),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')
        request = client.post('/confirmreset.json',
                              {'resetToken': token,
                               'password': new_password},
                              format='json')
        self.assertEqual(400, request.status_code)

        token = signing.dumps({'userId': str(uuid.uuid1()),
                               'rand': get_rand_str(16)},
                              salt='passwd_reset_req')
        request = client.post('/confirmreset.json',
                              {'resetToken': token,
                               'password': new_password},
                              format='json')
        self.assertEqual(404, request.status_code)

    def test_validate_email_view_set(self):
        client = APIClient()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)
        request = client.get('/confirmemail.json',
                             format='json')
        self.assertEqual(204, request.status_code)

        user_id = str_to_uuid1('7eff0578-6cb7-11e8-a2eb-acde48001122')
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)
        request = client.get('/confirmemail.json',
                             format='json')
        self.assertEqual(400, request.status_code)

        user_id = str_to_uuid1('83611214-6cb7-11e8-8334-acde48001122')
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)
        request = client.get('/confirmemail.json',
                             format='json')
        self.assertEqual(400, request.status_code)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_validate_email_view_set_error(self):
        client = APIClient()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        client.force_authenticate(user=user)
        request = client.get('/confirmemail.json',
                             format='json')
        self.assertEqual(500, request.status_code)

    def test_confirm_email_view_set(self):
        repo = MailVerificationRepository()
        user_id = str_to_uuid1('7a420db4-6cb7-11e8-9b1c-acde48001122')
        user = User.objects.get(id=user_id)
        (result, token) = repo.send_email_validation(user)
        self.assertEqual(1, result)

        self.assertEqual(False, user.validated_email)
        client = APIClient()
        client.force_authenticate(user=user)
        url = "/confirmemail/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(204, request.status_code)
        user = User.objects.get(id=user_id)
        self.assertEqual(True, user.validated_email)

        token = signing.dumps({'user': str(user.id),
                               'rand': get_rand_str(16)},
                              salt='verify_email_add')
        url = "/confirmemail/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(400, request.status_code)

        token = signing.dumps({'userId': str(uuid.uuid1()),
                               'rand': get_rand_str(16)},
                              salt='verify_email_add')
        url = "/confirmemail/{0}.json".format(token)
        request = client.get(url,
                             format='json')
        self.assertEqual(404, request.status_code)
