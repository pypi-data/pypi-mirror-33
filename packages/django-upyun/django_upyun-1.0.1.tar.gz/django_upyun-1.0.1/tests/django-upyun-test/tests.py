# -*- coding: utf-8 -*-

import os
import logging
import requests
from datetime import timedelta
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from django.conf import settings
from django.test import SimpleTestCase
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import timezone
from django.utils.timezone import is_naive, make_naive, utc
from django_upyun.backends import UpYunError, UpYunMediaStorage, UpYunStaticStorage, UpYunStorage, _get_config
from django_upyun import defaults

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logfile = os.path.join(os.getcwd(), 'test.log')
fh = RotatingFileHandler(logfile, mode='a', maxBytes=50 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


class TestUpYunStorage(SimpleTestCase):

    @contextmanager
    def save_file(self, name="test.txt", content=b"test", storage=default_storage):
        logging.info("name: %s", name)
        logging.debug("content: %s", content)
        name = storage.save(name, content)
        try:
            yield name
        finally:
            storage.delete(name)
            pass

    @contextmanager
    def create_dir(self, name="testdir/", storage=default_storage):
        logging.info("name: %s", name)
        name = storage.create_dir(name)
        try:
            yield name
        finally:
            pass

    def test_settings_mported(self):
        # Make sure bucket 'test-tmp-b1' exist under your UpYun account
        self.assertEqual(settings.UPY_SERVICE, "test-django-11111")
        with self.settings(UPY_SERVICE="test"):
            self.assertEqual(settings.UPY_SERVICE, "test")
        self.assertEqual(settings.UPY_SERVICE, "test-django-11111")

    def test_open_missing(self):
        self.assertFalse(default_storage.exists("test.txt"))
        self.assertRaises(UpYunError, lambda: default_storage.open("test.txt"))

    def test_open_writeMode(self):
        self.assertFalse(default_storage.exists("test.txt"))
        with self.save_file(name="test.txt"):
            self.assertTrue(default_storage.exists("test.txt"))
            self.assertRaises(ValueError, lambda: default_storage.open("test.txt", "wb"))

    def test_save_and_open(self):
        with self.save_file() as name:
            self.assertEqual(name, "test.txt")
            handle = default_storage.open(name)
            logging.info("handle: %s", handle)
            self.assertEqual(handle.read(), b"test")

    def test_save_and_open_cn(self):
        with self.save_file(content='我的座右铭'.encode('utf-8')) as name:
            self.assertEqual(name, "test.txt")
            handle = default_storage.open(name)
            logging.info("handle: %s", handle)
            self.assertEqual(handle.read().decode('utf-8'), '我的座右铭')

    def test_save_text_mode(self):
        with self.save_file(content=b"test"):
            self.assertEqual(default_storage.open("test.txt").read(), b"test")
            self.assertEqual(default_storage.content_type("test.txt"), "file")

    def test_save_small_file(self):
        with self.save_file():
            logging.info("content type: %s", default_storage.content_type("test.txt"))
            self.assertEqual(default_storage.open("test.txt").read(), b"test")
            self.assertEqual(requests.get(default_storage.url("test.txt")).content, b"test")

    def test_save_big_file(self):
        with self.save_file(content=b"test" * 1000):
            logging.info("content type: %s", default_storage.content_type("test.txt"))
            self.assertEqual(default_storage.open("test.txt").read(), b"test" * 1000)
            self.assertEqual(requests.get(default_storage.url("test.txt")).content, b"test" * 1000)

    def test_url(self):
        with self.save_file():
            url = default_storage.url("test.txt")
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], "text/plain")

    def test_url_cn(self):
        objname = "本地文件名.txt"
        # logging.info(f"objname: {objname}")
        with self.save_file(objname, content='我的座右铭'.encode('utf-8')) as name:
            self.assertEqual(name, objname)
            url = default_storage.url(objname)
            logging.info("url: %s", url)
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode('utf-8'), '我的座右铭')
            self.assertEqual(response.headers['Content-Type'], "text/plain")

    def test_exists(self):
        self.assertFalse(default_storage.exists("test.txt"))
        with self.save_file():
            self.assertTrue(default_storage.exists("test.txt"))
            self.assertFalse(default_storage.exists("fo"))

    def test_exists_long_path(self):
        self.assertFalse(default_storage.exists("admin/img/sorting-icons.svg"))
        with self.save_file("admin/img/sorting-icons.svg"):
            self.assertTrue(default_storage.exists("admin/img/sorting-icons.svg"))

    def test_create_dir(self):
        default_storage.delete("test3")
        self.assertFalse(default_storage.exists("test3"))
        with self.create_dir('test3/'):
            self.assertTrue(default_storage.exists("test3"))
            self.assertTrue(default_storage.exists("test3/"))
        default_storage.delete("test3/")
        self.assertFalse(default_storage.exists("test3/"))

    def test_exists_dir(self):
        default_storage.delete('test')
        default_storage.delete('test/')
        self.assertFalse(default_storage.exists("test"))
        self.assertFalse(default_storage.exists("test/"))
        with self.save_file(name="test/bar.txt"):
            self.assertTrue(default_storage.exists("test"))
            self.assertTrue(default_storage.exists("test/"))

    def test_size(self):
        with self.save_file():
            self.assertEqual(default_storage.size("test.txt"), 4)

    def test_delete(self):
        with self.save_file():
            self.assertTrue(default_storage.exists("test.txt"))
            default_storage.delete("test.txt")
        self.assertFalse(default_storage.exists("test.txt"))

    def test_get_modified_time(self):
        tzname = "Asia/Shanghai"
        with self.settings(USE_TZ=False, TIME_ZONE=tzname), self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertTrue(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)
        with self.settings(USE_TZ=True, TIME_ZONE=tzname), self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertFalse(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)
        with self.save_file():
            modified_time = default_storage.get_modified_time("test.txt")
            logging.info("modified time: %s", modified_time)
            logging.info("is naive: %s", is_naive(modified_time))
            self.assertFalse(is_naive(modified_time))
            # Check that the timestamps are roughly equals in the correct timezone
            self.assertLess(abs(modified_time - timezone.now()), timedelta(seconds=10))
            self.assertEqual(default_storage.get_accessed_time("test.txt"), modified_time)
            self.assertEqual(default_storage.get_created_time("test.txt"), modified_time)

    def test_listdir(self):
        default_storage.delete("test")
        self.assertFalse(default_storage.exists("test"))
        with self.save_file(), self.save_file(name="test/test.txt"):
            self.assertEqual(default_storage.listdir("."), (['media/test/'], ['media/test.txt']))
            self.assertEqual(default_storage.listdir("test"), ([], ['media/test/test.txt']))
            self.assertEqual(default_storage.listdir("test/"), ([], ['media/test/test.txt']))
            self.assertEqual(default_storage.listdir("test/test/"), ([], []))

    def test_endpoint_url(self):
        with self.settings(), self.save_file() as name:
            self.assertEqual(name, "test.txt")
            self.assertEqual(default_storage.open(name).read(), b"test")

    def test_overwrite(self):
        with self.save_file(content=b'aaaaaa') as name_1:
            self.assertEqual(name_1, "test.txt")
            handle = default_storage.open(name_1)
            content = handle.read()
            self.assertEqual(content, b"aaaaaa")
        with self.save_file(content=b'bbbbbb') as name_2:
            self.assertEqual(name_2, "test.txt")
            handle = default_storage.open(name_2)
            self.assertEqual(handle.read(), b"bbbbbb")

    def test_overwrite_cn(self):
        objname = "本地文件名.txt"
        # logging.info(f"objname: {objname}")
        with self.save_file(objname, content=u'我的座右铭'.encode('utf-8')) as name_1:
            self.assertEqual(name_1, objname)
            handle = default_storage.open(name_1)
            self.assertEqual(handle.read().decode('utf-8'), '我的座右铭')
        with self.save_file(objname, content=u'这是一个测试'.encode('utf-8')) as name_2:
            self.assertEqual(name_2, objname)
            handle = default_storage.open(name_2)
            self.assertEqual(handle.read().decode('utf-8'), '这是一个测试')

    def test_static_url(self):
        with self.save_file(storage=staticfiles_storage):
            url = staticfiles_storage.url("test.txt")
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], "text/plain")

    def test_configured_url(self):
        with self.settings(MEDIA_URL="/media/"), self.save_file():
            url = default_storage.url("test.txt")
            logging.info("url: %s", url)
            response = requests.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"test")
            self.assertEqual(response.headers['Content-Type'], "text/plain")

    def test_default_logger_basic(self):
        # verify default logger
        self.assertEqual(defaults.logger(), logging.getLogger())

        # verify custom logger
        custom_logger = logging.getLogger('test')
        defaults.log = custom_logger

        self.assertEqual(defaults.logger(), custom_logger)

    def test_initial_storage(self):
        # unconnect original DEFAULT_FILE_STORAGE
        with self.settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'):
            storage_with_populated_arguments = UpYunStorage(
                service=settings.UPY_SERVICE,
                username=settings.UPY_USERNAME,
                service_url=settings.UPY_SERVICE_URL,
                password=settings.UPY_PASSWORD)
            self.assertEqual(storage_with_populated_arguments.service,
                             settings.UPY_SERVICE)
            self.assertEqual(storage_with_populated_arguments.username,
                             settings.UPY_USERNAME)
            self.assertEqual(storage_with_populated_arguments.service_url,
                             settings.UPY_SERVICE_URL)
            self.assertEqual(storage_with_populated_arguments.password,
                             settings.UPY_PASSWORD)

            storage_with_default_arguments = UpYunStorage()
            self.assertEqual(storage_with_default_arguments.service,
                             settings.UPY_SERVICE)
            self.assertEqual(storage_with_default_arguments.username,
                             settings.UPY_USERNAME)
            self.assertEqual(storage_with_default_arguments.service_url,
                             settings.UPY_SERVICE_URL)
            self.assertEqual(storage_with_default_arguments.password,
                             settings.UPY_PASSWORD)

    def test_get_config(self):
        self.assertEqual(_get_config('UPY_USERNAME'), settings.UPY_USERNAME)

        # self.assertRaises(ImproperlyConfigured):
        #     _get_config('INVALID_ENV_VARIABLE_NAME')

