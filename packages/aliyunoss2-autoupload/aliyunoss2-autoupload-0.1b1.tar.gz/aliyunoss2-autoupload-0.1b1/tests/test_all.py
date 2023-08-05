from __future__ import absolute_import, unicode_literals, print_function

import os
import shutil
import sys
import unittest
from time import sleep

from dotenv import load_dotenv

from aliyunoss2_autoupload import conf, glb
from aliyunoss2_autoupload.performer import Performer

_PYTHON_VERSION_MAYOR_MINOR = '{0[0]}.{0[1]}'.format(sys.version_info)

load_dotenv()

str_ver = '{0[0]}.{0[1]}-{1}'.format(sys.version_info, sys.platform)


class OssAutoUploadTestCase(unittest.TestCase):
    def setUp(self):
        os.makedirs('tests/conf')
        cfg_files = {
            'log': 'tests/conf/log.yml',
            'prog': 'tests/conf/prog.yml',
        }
        for conf_name, conf_file in cfg_files.items():
            with open(conf_file, 'w') as f:
                conf.print_config(conf_name, f)
        conf.load_logging_config(cfg_files['log'])
        conf.load_program_config(cfg_files['prog'])
        # Fake OSS config
        glb.config['oss'] = dict(
            name=os.environ.get('OSS_NAME'),
            endpoint=os.environ.get('OSS_ENDPOINT'),
            access_key_id=os.environ.get('OSS_ACCESS_KEY_ID'),
            access_key_secret=os.environ.get('OSS_ACCESS_KEY_SECRET'),
        )
        #
        Performer.initial()

    def tearDown(self):
        Performer.release()
        shutil.rmtree('tests/conf')

    def test_upload_many(self):
        # Fake watcher config
        keys = []
        upload_dir = os.path.join('tests', 'uploads', str_ver)
        os.makedirs(upload_dir)
        for i in range(5):
            file_name = os.path.join(upload_dir, '{0}.dat'.format(i))
            keys.append(file_name)
        glb.config['watcher']['patterns'] = upload_dir + '/*.dat'
        glb.config['watcher']['write_complete_time'] = 0.1
        # generate a random binary file and upload
        try:
            for key in keys:
                with open(key, 'wb') as f:
                    f.write(os.urandom(1024))  # replace 1024 with size_kb if not unreasonably large
            # wait for `write_complete_time`
            sleep(0.1)
            # scan and upload
            Performer.run_once()
        finally:
            shutil.rmtree(upload_dir)

        # check if uploaded path ok
        bucket = Performer._get_oss_bucket()
        for key in keys:
            self.assertTrue(bucket.object_exists(key))
        bucket.batch_delete_objects(keys)

    if _PYTHON_VERSION_MAYOR_MINOR >= '3.5':

        def test_upload_recursive(self):
            # Fake watcher config
            keys = []
            upload_dir = os.path.join('tests', 'uploads', str_ver)
            os.makedirs(upload_dir)
            for i in range(3):
                file_name = os.path.join(upload_dir, '{0}.dat'.format(i))
                keys.append(file_name)
                for j in range(2):
                    dir_name = os.path.join(upload_dir, '{0}'.format(i))
                    file_name = os.path.join(dir_name, '{0}.dat'.format(j))
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                    keys.append(file_name)
            glb.config['watcher']['patterns'] = upload_dir + '/**/*.dat'
            glb.config['watcher']['recursive'] = True
            glb.config['watcher']['write_complete_time'] = 0.1
            # generate a random binary file and upload
            try:
                for key in keys:
                    with open(key, 'wb') as f:
                        f.write(os.urandom(1024))  # replace 1024 with size_kb if not unreasonably large
                # wait for `write_complete_time`
                sleep(1)
                # scan and upload
                Performer.run_once()
            finally:
                shutil.rmtree(upload_dir)

            # check if uploaded path ok
            bucket = Performer._get_oss_bucket()
            for key in keys:
                self.assertTrue(bucket.object_exists(key))
            bucket.batch_delete_objects(keys)


if __name__ == '__main__':
    unittest.main()
