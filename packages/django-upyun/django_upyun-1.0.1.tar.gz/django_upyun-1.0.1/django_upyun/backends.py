# coding=utf-8

import os
import time
from datetime import datetime
from tempfile import SpooledTemporaryFile
from urllib.parse import urljoin

import upyun
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text
from django.utils.timezone import utc
from upyun import UpYunClientException, UpYunServiceException

from .defaults import logger


def _get_config(name, default=None):
    config = os.environ.get(name, getattr(settings, name, default))
    if config is not None:
        if isinstance(config, str):
            return config.strip()
        else:
            return config
    else:
        raise ImproperlyConfigured("'%s not found in env variables or setting.py" % name)


def _normalize_endpoint(endpoint):
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        return 'https://' + endpoint
    else:
        return endpoint


class UpYunError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


@deconstructible
class UpYunStorage(Storage):
    """
    UpYun Storage
    """

    def path(self, name):
        return name

    def __init__(self, service=None, username=None, password=None, service_url=None,
                 need_coverage=False, save_full_url=False):
        self.service = service if service else _get_config('UPY_SERVICE')
        self.username = username if username else _get_config('UPY_USERNAME')
        self.password = password if password else _get_config('UPY_PASSWORD')
        self.service_url = service_url if service_url else _get_config('UPY_SERVICE_URL')
        self.need_coverage = need_coverage if need_coverage else _get_config('UPY_NEED_COVERAGE')
        self.save_full_url = save_full_url if save_full_url else _get_config('UPY_SAVE_FULL_URL')

        if not self.service_url or not self.service_url.startswith('http'):
            raise ImproperlyConfigured("'%s must start with http protocol." % self.need_coverage)

        self.up = upyun.UpYun(self.service, self.username, self.password, timeout=30, endpoint=upyun.ED_AUTO)

    def _get_key_name(self, name):
        """
        Get the object key name in Storage, e.g.,
        location: /media/
        input   : test.txt
        output  : media/test.txt
        """
        if name.startswith(self.service_url):
            return self.url2key(name)

        base_path = force_text(self.location)
        final_path = urljoin(base_path + "/", name)
        name = os.path.normpath(final_path.lstrip('/'))

        # Add / to the end of path since os.path.normpath will remove it
        if final_path.endswith('/') and not name.endswith('/'):
            name += '/'

        logger().debug("target name: %s", name)
        return name

    def _open(self, name, mode='rb'):
        logger().debug("name: %s, mode: %s", name, mode)
        if mode != "rb":
            raise ValueError("files can only be opened in read-only mode")

        target_name = self._get_key_name(name)
        logger().debug("target name: %s", target_name)
        try:
            # Load the key into a temporary file
            tmpf = SpooledTemporaryFile(max_size=10 * 1024 * 1024)  # 10MB
            s = self.up.get(target_name)
            tmpf.write(s.encode())
            tmpf.seek(0)
            return UpYunFile(tmpf, target_name, self)
        except (UpYunClientException,):
            raise UpYunError(f"{name} get error")
        except:
            raise UpYunError(f"Failed to open {name}")

    def _save(self, name, content):
        if self.exists(name):
            if self.need_coverage:
                self.delete(name)
            else:
                file_name, ext = os.path.splitext(name)
                if ext:
                    name = f"{file_name}_{time.time()}{ext}"
                else:
                    name = f"{file_name}_{time.time()}"

        target_name = self._get_key_name(name)
        logger().debug("target name: %s", target_name)
        logger().debug("content: %s", content)
        self.up.put(target_name, content)

        if self.save_full_url is True:
            return self.url(name)
        return os.path.normpath(name)

    def create_dir(self, dirname):
        target_name = self._get_key_name(dirname)
        if not target_name.endswith('/'):
            target_name += '/'

        self.up.mkdir(target_name)

    def exists(self, name):
        target_name = self._get_key_name(name)
        logger().debug("name: %s, target name: %s", name, target_name)
        try:
            msg = self.up.getinfo(target_name)
            if msg['file-type'] == 'folder':
                pass
            return True
        except UpYunServiceException as e:
            if e.status == 404:
                return False

        return False

    def get_file_meta(self, name):
        name = self._get_key_name(name)
        res = self.up.getinfo(name)
        return res['file-type']

    def size(self, name):
        name = self._get_key_name(name)
        res = self.up.getinfo(name)
        return int(res['file-size'])

    def get_modified_time(self, name):
        name = self._get_key_name(name)
        res = self.up.getinfo(name)
        t = int(res['file-date'])
        if settings.USE_TZ:
            return datetime.utcfromtimestamp(t).replace(tzinfo=utc)
        else:
            return datetime.fromtimestamp(t)

    get_created_time = get_accessed_time = get_modified_time

    def content_type(self, name):
        return self.get_file_meta(name=name)

    def listdir(self, name):
        if name == ".":
            name = ""
        name = self._get_key_name(name)
        if not name.endswith('/'):
            name += "/"
        logger().debug("name: %s", name)

        res = self.up.getlist(name)
        files = []
        dirs = []

        for obj in res:
            if obj['type'] == 'F':
                dirs.append(f"{name}{obj['name']}")
            elif obj['type'] == 'N':
                files.append(f"{name}{obj['name']}")

        logger().debug("dirs: %s", list(dirs))
        logger().debug("files: %s", files)
        return dirs, files

    def url2key(self, url):
        # 翻转url函数的结果
        if url.startswith(self.service_url):
            if self.service_url.endswith('/'):
                return url.replace(self.service_url, '')
            return url.replace(self.service_url + '/', '')
        return url

    def url(self, name):
        if name.startswith('http'):
            return name
        key = self._get_key_name(name)
        return urljoin(self.service_url, key)

    # f_type: N 表示文件，F 表示目录。
    def delete(self, name, f_type='N'):
        # 删除又拍云上的文件或者文件夹
        name = self._get_key_name(name)
        logger().debug("delete name: %s", name)
        if f_type == 'F':
            # 注意删除目录时，必须保证目录为空。
            dirs, files = self.listdir(name)
            for file in files:
                self.delete(file, 'N')
            for dr in dirs:
                self.delete(dr, 'F')
        try:
            self.up.delete(name)
            return True
        except UpYunServiceException as e:
            if e.status == 404:
                return True
        return False


class UpYunMediaStorage(UpYunStorage):
    def __init__(self):
        self.location = settings.MEDIA_URL
        logger().debug("locatin: %s", self.location)
        super(UpYunMediaStorage, self).__init__()

    def save(self, name, content, max_length=None):
        return super()._save(name, content)


class UpYunStaticStorage(UpYunStorage):
    def __init__(self):
        self.location = settings.STATIC_URL
        logger().info("locatin: %s", self.location)
        super(UpYunStaticStorage, self).__init__()

    def save(self, name, content, max_length=None):
        return super(UpYunStaticStorage, self)._save(name, content)


class UpYunFile(File):
    """
    A file returned from UpYun
    """

    def __init__(self, content, name, storage):
        super().__init__(content, name)
        self._storage = storage

    def open(self, mode="rb"):
        if self.closed:
            self.file = self._storage.open(self.name, mode).file
        return super().open(mode)
