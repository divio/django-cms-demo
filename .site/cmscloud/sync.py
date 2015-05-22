# -*- coding: utf-8 -*-
import fcntl
import hashlib
import hmac
import os
import sys
import tarfile

from django.core.files.temp import NamedTemporaryFile
from django.utils.crypto import constant_time_compare
from itsdangerous import URLSafeTimedSerializer
from raven.contrib.django.models import get_client
import requests


COMMIT_CACHE_FILEPATH = os.path.join(
    os.path.dirname(__file__), '.sync_commit_cache')
CHUNK_SIZE = 64 * 1024  # 64KB


def sync_changed_files(sync_key, last_commit_hash, sync_url, project_dir):
    try:
        _sync_changed_files(sync_key, last_commit_hash, sync_url, project_dir)
    except Exception:
        import traceback
        traceback.print_exc()
        exc_info = sys.exc_info()
        try:
            raven_client = get_client()
            raven_client.captureException(exc_info=exc_info)
        except:
            import traceback
            traceback.print_exc()
            pass


def _sync_changed_files(sync_key, last_commit_hash, sync_url, project_dir):
    if not os.path.exists(COMMIT_CACHE_FILEPATH):
        open(COMMIT_CACHE_FILEPATH, 'w').close()
    commit_cache_file = open(COMMIT_CACHE_FILEPATH, 'r+')
    fd = commit_cache_file.fileno()
    temp_file = None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as e:
        print "other process is already running the sync:\n%s" % repr(e)
    else:
        last_commit_hash_from_cache = commit_cache_file.read()
        if last_commit_hash_from_cache:
            last_commit_hash = last_commit_hash_from_cache
        temp_file = NamedTemporaryFile(prefix='sync_changed_files', suffix='.tar.gz')
        signer = URLSafeTimedSerializer(sync_key)
        signed_data = signer.dumps(last_commit_hash)
        data = {'last_commit_hash': signed_data}
        response = requests.post(sync_url, data=data, stream=True)
        if response.ok:
            data_signature = hmac.new(key=str(sync_key), digestmod=hashlib.sha1)
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                data_signature.update(chunk)
                temp_file.write(chunk)
            temp_file.seek(0)
            data_signature = data_signature.hexdigest()
            header_signature = response.headers.get('aldryn-sync-signature')
            if not constant_time_compare(header_signature, data_signature):
                # TODO log failed attempt to corrupt the website's data
                raise RuntimeError(
                    'Sync signatures does not match:\ndata:\t%s\nheader:\t%s' %
                    (data_signature, header_signature))
            tarball = tarfile.open(mode='r:gz', fileobj=temp_file)
            for member in tarball.getmembers():
                path = member.name
                if path.startswith(('static/', 'templates/')):
                    full_path = os.path.join(project_dir, path)
                    directory = os.path.dirname(full_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    tarball.extract(member, project_dir)
            tarball.close()
            # Successfully synced files, storing the newest commit hash
            current_commit_hash = response.headers.get(
                'aldryn-sync-current-commit', last_commit_hash)
            commit_cache_file.seek(0)
            commit_cache_file.truncate()
            commit_cache_file.write(current_commit_hash)
        else:
            response.raise_for_status()
    finally:
        commit_cache_file.close()
        if temp_file:
            temp_file.close()
