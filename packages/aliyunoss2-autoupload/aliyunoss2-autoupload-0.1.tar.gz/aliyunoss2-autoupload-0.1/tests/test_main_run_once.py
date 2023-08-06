from __future__ import absolute_import, print_function

import errno
import io
import os
import shutil
import sys
import unittest

import yaml
from dotenv import load_dotenv

from aliyunoss2_autoupload import __main__ as main_module
from aliyunoss2_autoupload import conf
from aliyunoss2_autoupload.performer import Performer
from aliyunoss2_autoupload.utils.strhelper import to_unicode

_PYTHON_VERSION_MAYOR_MINOR = '{0[0]}.{0[1]}'.format(sys.version_info)

if _PYTHON_VERSION_MAYOR_MINOR <= '2.7':
    from pathlib2 import Path
else:
    from pathlib import Path

load_dotenv()

str_ver = '{0[0]}.{0[1]}-{1}'.format(sys.version_info, sys.platform)


class MainRunOnceTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainRunOnceTestCase, self).__init__(*args, **kwargs)
        self.conf_buf = None  # type: io.StringIO
        self.files = []

    def setUp(self):
        # Fake arguments
        main_module.parse_arguments(['run', '--only-once'])

        # log.yml
        log_conf_buf = io.StringIO()
        conf.print_config('log', log_conf_buf)
        log_conf_buf.seek(0)
        main_module._arguments.logging_config_file = log_conf_buf

        # prog.yml
        with io.StringIO() as stream:
            conf.print_config('prog', stream)
            self.conf_data = yaml.safe_load(stream.getvalue())
        # Fake OSS config
        self.conf_data['oss'] = dict(
            name=os.environ.get('OSS_NAME'),
            endpoint=os.environ.get('OSS_ENDPOINT'),
            access_key_id=os.environ.get('OSS_ACCESS_KEY_ID'),
            access_key_secret=os.environ.get('OSS_ACCESS_KEY_SECRET'),
        )
        self.conf_data['watcher'] = dict(
            write_complete_time=0.1
        )
        # Fake load
        self.set_conf_data()

    def tearDown(self):
        # check if uploaded path ok
        bucket = Performer._get_oss_bucket()
        for key in self.files:
            self.assertTrue(bucket.object_exists(key))
        bucket.batch_delete_objects(self.files)
        # release
        Performer.release()

    def set_conf_data(self):
        self.conf_buf = io.StringIO(to_unicode(yaml.safe_dump(self.conf_data)))
        self.conf_buf.seek(0)
        main_module._arguments.config_file = self.conf_buf

    def generate_files(self):
        for file in self.files:
            path = Path(file)
            try:
                path.parent.mkdir(parents=True)
            except Exception as err:
                if _PYTHON_VERSION_MAYOR_MINOR <= '2.7':
                    if isinstance(err, OSError):
                        if err.errno != errno.EEXIST:
                            raise
                    else:
                        raise
                else:
                    if not isinstance(err, FileExistsError):
                        raise
            with open(file, 'wb') as f:
                f.write(os.urandom(1024))  # replace 1024 with size_kb if not unreasonably large

    def run_main_func(self, remove_dir=''):
        self.set_conf_data()
        try:
            # generate a random binary files
            self.generate_files()
            # scan and upload
            main_module.main()
        finally:
            if remove_dir:
                shutil.rmtree(remove_dir)

    def test_upload_many(self):
        # Fake watcher config
        self.files = []
        upload_dir = os.path.join('tests', 'uploads', str_ver)
        for i in range(5):
            file_name = os.path.join(upload_dir, '{0}.dat'.format(i))
            self.files.append(file_name)
        self.conf_data['watcher']['patterns'] = upload_dir + '/*.dat'
        # generate a random binary file and upload
        self.run_main_func(upload_dir)

    if _PYTHON_VERSION_MAYOR_MINOR >= '3.5':

        def test_upload_recursive(self):
            # Fake watcher config
            self.files = []
            upload_dir = os.path.join('tests', 'uploads', str_ver)
            for i in range(3):
                file_name = os.path.join(upload_dir, '{0}.dat'.format(i))
                self.files.append(file_name)
                for j in range(2):
                    dir_name = os.path.join(upload_dir, '{0}'.format(i))
                    file_name = os.path.join(dir_name, '{0}.dat'.format(j))
                    self.files.append(file_name)
            self.conf_data['watcher']['patterns'] = upload_dir + '/**/*.dat'
            self.conf_data['watcher']['recursive'] = True
            # generate a random binary file and upload
            self.run_main_func(upload_dir)


if __name__ == '__main__':
    unittest.main()
