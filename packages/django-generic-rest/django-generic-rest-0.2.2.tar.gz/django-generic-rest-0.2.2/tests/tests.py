import uuid

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.hashers import check_password

from rest_framework.test import APIClient

from utility.exceptions import ObjectNotFoundError, ValidationError
from utility.functions import str_to_uuid1
from authentication.models import User
from tests.models import Object, UserObject, UserObjectPw
from generic.factories import generic_factory
from generic.validators import is_value_unique, validate_many
from generic.repositories import GenericRepository
from generic.services import (generic_retrieve_single_service,
                              generic_retrieve_all_service,
                              generic_delete_service,
                              generic_update_service,
                              generic_create_service)


class GenericFactoryTest(TransactionTestCase):
    def test_factory(self):
        name = 'new object'
        kwargs = {'name': name}
        o = generic_factory(model_class = Object, **kwargs)
        self.assertEqual(Object, type(o))
        self.assertEqual(type(uuid.uuid1()), type(o.id))
        self.assertEqual(name, o.name)


class GenericRepositoryTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_find_by_user(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o1 = u.user_objects.all()[0]
        o2 = repo.find_by_user(u)[0]
        self.assertEqual(o1, o2)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l = len(list(repo.find_by_user(u)))
        self.assertEqual(0, l)

    def test_find_by_id(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        o1 = UserObject.objects.get(id=o_id)
        o2 = list(repo.find_by_id(pk=o_id, user=u))[0]
        self.assertEqual(o1, o2)

        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('87eca58a-5f71-11e8-b471-f40f2434c1ce')
        l = len(list(repo.find_by_id(pk=o_id, user=u)))
        self.assertEqual(0, l)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('4343f01c-5f71-11e8-b73c-f40f2434c1ce')
        o1 = Object.objects.get(id=o_id)
        o2 = list(repo.find_by_id(pk=o_id, user=u))
        self.assertEqual(0, len(o2))

    def test_get_by_id(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        o1 = UserObject.objects.get(id=o_id)
        o2 = repo.get_by_id(pk=o_id, user=u)
        self.assertEqual(o1, o2)

        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('87eca58a-5f71-11e8-b471-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            repo.get_by_id(pk=o_id, user=u)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('4343f01c-5f71-11e8-b73c-f40f2434c1ce')
        o1 = Object.objects.get(id=o_id)
        with self.assertRaises(ObjectNotFoundError):
            o2 = repo.get_by_id(pk=o_id, user=u)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('e488a5ba-5f78-11e8-b89d-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            o = repo.get_by_id(pk=o_id, user=u)

    def test_get_by_user_and_id(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        o1 = UserObject.objects.get(id=o_id)
        o2 = repo.get_by_user_and_id(pk=o_id, user=u)
        self.assertEqual(o1, o2)

        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('87eca58a-5f71-11e8-b471-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            o = repo.get_by_user_and_id(pk=o_id, user=u)

        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('fd88db5e-5f82-11e8-a7f9-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            o = repo.get_by_user_and_id(pk=o_id, user=u)

    def test_get_all(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l1 = len(list(UserObject.objects.filter(owner=u)))
        l2 = len(list(repo.get_all(user=u)))
        self.assertEqual(l1, l2)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l2 = len(list(repo.get_all(user=u)))
        self.assertEqual(0, l2)

    def test_persist(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l1 = len(list(UserObject.objects.filter(owner=u)))
        instance = UserObject(name='A new user object', owner=u)
        repo.persist(instance)
        l2 = len(list(UserObject.objects.filter(owner=u)))
        self.assertEqual(l1, (l2-1))

    def test_delete_by_id(self):
        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l1 = len(list(UserObject.objects.filter(owner=u)))
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        repo.delete_by_id(pk=o_id, user=u)
        l2 = len(list(UserObject.objects.filter(owner=u)))
        self.assertEqual(l1, (l2+1))

        repo = GenericRepository(UserObject)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l1 = len(list(UserObject.objects.filter(owner=u)))
        o_id = str_to_uuid1('87eca58a-5f71-11e8-b471-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            repo.delete_by_id(pk=o_id, user=u)

        repo = GenericRepository(Object)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        l1 = len(list(Object.objects.all()))
        o_id = str_to_uuid1('6ef912ae-5f71-11e8-bc5f-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            repo.delete_by_id(pk=o_id, user=u)

    def test_check_unique(self):
        repo = GenericRepository(Object)
        o_id = str_to_uuid1('0b8d3a45-5f77-11e8-a826-f40f2434c1ce')
        unique = len(list(repo.check_unique(o_id, 'name', 'Object')))
        self.assertEqual(1, unique)

        repo = GenericRepository(Object)
        o_id = str_to_uuid1('0b8d3a45-5f77-11e8-a826-f40f2434c1ce')
        unique = len(list(repo.check_unique(o_id, 'name', 'NewObjectName')))
        self.assertEqual(0, unique)

        repo = GenericRepository(Object)
        o_id = str_to_uuid1('4343f01c-5f71-11e8-b73c-f40f2434c1ce')
        unique = len(list(repo.check_unique(o_id, 'name', 'Object')))
        self.assertEqual(0, unique)

        repo = GenericRepository(Object)
        o_id = str_to_uuid1('0b8d3a45-5f77-11e8-a826-f40f2434c1ce')
        unique = repo.check_unique(o_id, 'name', None)
        self.assertEqual(0, unique)

    def test_check_password_too_short(self):
        repo = GenericRepository(Object)
        too_short = repo.check_password_too_short('123', 3)
        self.assertEqual(False, too_short)

        too_short = repo.check_password_too_short('123', 4)
        self.assertEqual(True, too_short)

    def test_check_too_few_char_classes(self):
        repo = GenericRepository(Object)
        classes = repo.check_too_few_char_classes('123', 1)
        self.assertEqual(False, classes)

        classes = repo.check_too_few_char_classes('123', 2)
        self.assertEqual(True, classes)

        repo = GenericRepository(Object)
        classes = repo.check_too_few_char_classes('123Abc', 3)
        self.assertEqual(False, classes)

        classes = repo.check_too_few_char_classes('123Abc', 4)
        self.assertEqual(True, classes)

    def test_check_email_valid(self):
        repo = GenericRepository(Object)
        valid = repo.check_email_valid('john.doe@example.at')
        self.assertEqual(True, valid)

        repo = GenericRepository(Object)
        valid = repo.check_email_valid('johndoe@exampleat')
        self.assertEqual(False, valid)

        repo = GenericRepository(Object)
        valid = repo.check_email_valid('john.doe.example.at')
        self.assertEqual(False, valid)

        repo = GenericRepository(Object)
        valid = repo.check_email_valid('john.doe@example')
        self.assertEqual(False, valid)

        repo = GenericRepository(Object)
        valid = repo.check_email_valid('@example.at')
        self.assertEqual(False, valid)


class GenericValidatorTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_is_value_unique(self):
        repo = GenericRepository(Object)
        o_id = str_to_uuid1('6ef912ae-5f71-11e8-bc5f-f40f2434c1ce')
        o = Object.objects.get(id=o_id)

        validator = is_value_unique(repo, 'name')
        self.assertEqual(True, validator(o))

        repo = GenericRepository(Object)
        o = Object(name='Object')

        validator = is_value_unique(repo, 'name')
        with self.assertRaises(ValidationError):
            validator(o)

        repo = GenericRepository(Object)
        os = Object.objects.all()

        validator = is_value_unique(repo, 'name')
        self.assertEqual(True, validator(os))

    def test_validate_many(self):
        repo = GenericRepository(UserObject)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        o = UserObject.objects.get(id=o_id)

        validators = (is_value_unique(repo, 'name'),
                      is_value_unique(repo, 'owner_id'))
        checker = validate_many(*validators)
        self.assertEqual(True, checker(o))


class GenericServiceTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_retrieve_single_service(self):
        repo = GenericRepository(Object)
        retrieve = generic_retrieve_single_service(repo)
        o_id = str_to_uuid1('6ef912ae-5f71-11e8-bc5f-f40f2434c1ce')
        with self.assertRaises(ObjectNotFoundError):
            o = retrieve(pk=o_id, user=None)

    def test_retrieve_all_service(self):
        repo = GenericRepository(Object)
        retrieve = generic_retrieve_all_service(repo)
        with self.assertRaises(ObjectNotFoundError):
            o_list = retrieve(user=None)

    def test_delete_service(self):
        repo = GenericRepository(Object)
        delete = generic_delete_service(repo)
        o_id = str_to_uuid1('6ef912ae-5f71-11e8-bc5f-f40f2434c1ce')
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o1 = Object.objects.get(id=o_id)
        with self.assertRaises(ObjectNotFoundError):
            o2 = delete(pk=o_id, user=u)

        repo = GenericRepository(UserObject)
        delete = generic_delete_service(repo)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o1 = UserObject.objects.get(id=o_id)
        o2 = delete(pk=o_id, user=u)
        o_l = len(list(UserObject.objects.filter(id=o_id)))
        self.assertEqual(0, o_l)

        repo = GenericRepository(UserObject)
        delete = generic_delete_service(repo)
        o_id = str_to_uuid1('87eca58a-5f71-11e8-b471-f40f2434c1ce')
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o1 = UserObject.objects.get(id=o_id)
        with self.assertRaises(ObjectNotFoundError):
            o2 = delete(pk=o_id, user=u)

    def test_update_service(self):
        repo = GenericRepository(Object)
        validator = (is_value_unique(repo, 'name'),)
        update = generic_update_service(repo, validate_many(*validator))
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('6ef912ae-5f71-11e8-bc5f-f40f2434c1ce')
        name = 'NewNameForOldObject'
        password = 'newSecure#1Pass'

        with self.assertRaises(ObjectNotFoundError):
            update(pk=o_id, user=u, name=name, password=password)

        repo = GenericRepository(UserObject)
        validator = (is_value_unique(repo, 'name'),)
        update = generic_update_service(repo, validate_many(*validator))
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('83695382-5f71-11e8-9d7e-f40f2434c1ce')
        name='NewNameForOldObject'

        update(pk=o_id, user=u, name=name)
        o = UserObject.objects.get(id=o_id)
        self.assertEqual(o_id, o.id)
        self.assertEqual(name, o.name)

        repo = GenericRepository(UserObjectPw)
        validator = (is_value_unique(repo, 'name'),)
        update = generic_update_service(repo, validate_many(*validator))
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o_id = str_to_uuid1('603378ab-5f85-11e8-8ef9-f40f2434c1ce')
        name = 'NewNameForOldObject'
        password = 'NewSecurePassword#123'

        update(pk=o_id, user=u, name=name, password=password)
        o = UserObjectPw.objects.get(id=o_id)
        self.assertEqual(o_id, o.id)
        self.assertEqual(name, o.name)
        self.assertEqual(True, check_password(password, o.password))

    def test_create_service(self):
        repo = GenericRepository(Object)
        validator = (is_value_unique(repo, 'name'),)
        create = generic_create_service(repo,
                                        validate_many(*validator),
                                        generic_factory)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        password = 'New123Password'
        o1 = create(user=u, name='VeryNewObject', password=password)
        o2 = Object.objects.get(id=o1.id)
        self.assertEqual(o1, o2)
        self.assertEqual(True, check_password(password, o1.password))
        self.assertEqual(True, check_password(password, o2.password))

        repo = GenericRepository(UserObject)
        validator = (is_value_unique(repo, 'name'),)
        create = generic_create_service(repo,
                                        validate_many(*validator),
                                        generic_factory)
        user_id = str_to_uuid1('3f44d78a-1c69-11e8-a078-f40f2434c1ce')
        u = User.objects.get(id=user_id)
        o1 = create(user=u, name='VeryNewObject')
        o2 = UserObject.objects.get(id=o1.id)
        self.assertEqual(o1, o2)


class GenericViewTest(TransactionTestCase):
    fixtures = ['init.json']

    def test_create_view(self):
        user = User.objects.get(username='lisamorgan')
        client = APIClient()
        client.force_authenticate(user=user)

        l1 = len(list(UserObject.objects.all()))
        request = client.post('/objects.json', {'name': 'new name'}, format='json')
        l2 = len(list(UserObject.objects.all()))
        self.assertEqual(201, request.status_code)
        self.assertEqual(l1, (l2-1))

    def test_list_view(self):
        user = User.objects.get(username='lisamorgan')
        client = APIClient()
        client.force_authenticate(user=user)

        request = client.get('/objects.json', format='json')
        self.assertEqual(200, request.status_code)

    def test_retrieve_view(self):
        user = User.objects.get(username='lisamorgan')
        client = APIClient()
        client.force_authenticate(user=user)

        request = client.get('/objects/83695382-5f71-11e8-9d7e-f40f2434c1ce.json', format='json')
        self.assertEqual(200, request.status_code)

    def test_destroy_view(self):
        user = User.objects.get(username='lisamorgan')
        client = APIClient()
        client.force_authenticate(user=user)

        l1 = len(list(UserObject.objects.all()))
        request = client.delete('/objects/83695382-5f71-11e8-9d7e-f40f2434c1ce.json', format='json')
        l2 = len(list(UserObject.objects.all()))
        self.assertEqual(200, request.status_code)
        self.assertEqual(l1, (l2+1))

    def test_partial_update_view(self):
        user = User.objects.get(username='lisamorgan')
        client = APIClient()
        client.force_authenticate(user=user)

        request = client.patch('/objects/83695382-5f71-11e8-9d7e-f40f2434c1ce.json', {'name': 'new name2'}, format='json')
        self.assertEqual(200, request.status_code)