# -*- coding: utf8 -*-
import collections
import json
import logging
import time

from concurrent.futures import ThreadPoolExecutor

from .download_entity import DownloadEntity
from .metadata_files import MetadataFiles

try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle

import random
import string
import tempfile
from contextlib import closing
import sys
import os
from uuid import uuid4
import datetime
from six import wraps
from .api import default_api_retry
from .json_utils import multi_line_json_from_data, normalize_item, dict_normalize
from . import MetadataOperationError
from .multi_process_control import get_multi_process_control
from .path_utils import get_batch_of_files_from_paths, safe_make_dirs, DestPathEnum, enumerate_paths_with_info
from .print_status import PrintStatus
from .eprint import eprint


def wrap_exceptions(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AssertionError:
            raise
        except Exception as ex:
            eprint('\n' + str(ex))
            sys.exit(1)

    return decorated


epoch = datetime.datetime.utcfromtimestamp(0)


class InvalidJsonFile(Exception):
    def __init__(self, filename, ex):
        self.filename = filename
        self.ex = ex


def _download_entity(config_init_dict, volume_id, metadata, headers):
    return DownloadEntity.download(config_init_dict, volume_id, metadata, headers)


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def status_with_timing(message, callback, fp=sys.stdout, on_summery_data=None):
    start_time = datetime.datetime.utcnow()
    status_line = PrintStatus(fp=fp)
    with closing(status_line):
        status_line.print_status(message)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callback)

            while future.running():
                total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)
                status_line.print_status("%s %s" % (message, total_time))

                time.sleep(0.1)

            result = future.result()
            total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)

            if on_summery_data is not None:
                summery_data = on_summery_data(result)
                summery_data = '%s, %s' % (total_time, summery_data)
            else:
                summery_data = str(total_time)

            status_line.print_status('%s Done (%s)' % (message, summery_data))

    return result


def disk_result(resume_token, method, result_callback=None):
    def wrap_f(f):
        def wrap(*args, **kwargs):
            import tempfile

            def loader():
                cache_result = pickle.load(cache_file)
                if result_callback is not None:
                    result_callback(cache_result)

                return cache_result

            name = '{func_name}_{python_version}'.format(func_name=method, python_version=sys.hexversion)
            full_path = os.path.join(tempfile.gettempdir(), 'ml_cache', resume_token, name)

            try:
                with open(full_path, 'rb') as cache_file:
                    return status_with_timing('Loading cache file', loader)
            except IOError:
                pass
            except Exception as ex:
                logging.debug('failed to load %s %s', full_path, ex)

            result = f(*args, **kwargs)

            full_path_tmp = full_path + '.tmp'
            try:
                safe_make_dirs(os.path.dirname(full_path_tmp))
                with open(full_path_tmp, 'wb') as cache_file:
                    pickle.dump(result, cache_file, pickle.HIGHEST_PROTOCOL)
                    os.rename(full_path_tmp, full_path)
            except Exception as ex:
                logging.info('failed to save %s %s', full_path_tmp, ex)

            return result

        return wrap

    return wrap_f


class DiskStorage(object):
    def __init__(self, dest_pattern, save_meta):
        self.__dest_pattern = dest_pattern
        self.__save_meta = save_meta

    def close(self):
        pass

    def add_item(self, metadata, data):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        safe_make_dirs(os.path.dirname(full_filename))

        if self.__save_meta:
            item_meta = {key: val for key, val in metadata.items() if not key.startswith('@')}
            with open(full_filename + '.metadata.json', 'w') as f:
                json.dump(item_meta, f)

        with open(full_filename, 'wb') as f:
            f.write(data)

    def has_item(self, metadata):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        return os.path.isfile(full_filename)

    @property
    def storage_params(self):
        return {
            'dest_pattern': self.__dest_pattern,
            'save_meta': self.__save_meta,
        }

    # noinspection PyUnusedLocal
    @classmethod
    def init_from_config(cls, dest_pattern, save_meta, **kwargs):
        return cls(dest_pattern, save_meta)


class DataSync(object):
    resume_prefix = 'resume-'

    def __init__(self, ctx, repo, no_progressbar, resume_token=None):
        self.__ctx = ctx
        self.__repo = repo
        self.__no_progressbar = no_progressbar

        self.__resume_token = resume_token or self.generate_resume_token()

        if not self.__resume_token.startswith(self.resume_prefix):
            self.__resume_token = self.resume_prefix + self.__resume_token

    @property
    def repo(self):
        return self.__repo

    @property
    def resume_token(self):
        return self.__resume_token

    def __upload_file_for_processing(self, file_obj, file_description):
        from .gcs_utils import do_upload
        from tqdm import tqdm

        volume_id = self.__repo.data_volume_config.volume_id

        data_object_name = '%s/temp/%s_%s.json' % (volume_id, file_description, uuid4().hex)

        url = 'data_volumes/{volume_id}/gcs_urls'.format(volume_id=volume_id)

        headers = {'Content-Type': 'application/json'}

        msg = {
            'methods': 'PUT',
            'paths': [data_object_name],
            'content_type': 'application/json',
            'temp': True,
        }

        result = self.__ctx.obj.handle_api(self.__ctx.obj, self.__ctx.obj.session, 'post', url, msg, retry=default_api_retry())

        put_url = result['put'][0]

        gcs_auth = self.__repo.data_volume_config.object_store_config.get('auth')

        def update_bar(c):
            bar.update(c)

        logging.debug('uploading %s', data_object_name)
        with tqdm(total=file_obj.tell(), desc="Uploading {}".format(file_description), unit=' KB', ncols=80,
                  disable=self.__no_progressbar, unit_scale=True) as bar:
            do_upload(gcs_auth, None, data_object_name, file_obj, headers, head_url=None, put_url=put_url,
                      callback=update_bar)

        return data_object_name

    def __process_index(self, object_name, isolation_token):
        index = self.__repo.open_index()

        def get_changeset():
            return index.get_changeset('gs://' + object_name, isolation_token)

        change_set = status_with_timing('Server process index', get_changeset)

        total_modify_files = 0
        total_new_files = 0

        files_to_upload = tempfile.TemporaryFile('w+')

        for name, op in change_set:
            if op == 'm':
                total_modify_files += 1
            elif op == 'i':
                total_new_files += 1
            else:
                continue

            data = name + '\n'

            files_to_upload.write(data)

        total_files_to_upload = total_modify_files + total_new_files
        files_to_upload.seek(0)

        return files_to_upload, total_files_to_upload

    def upload_and_update_index(self, index_entities_file, isolation_token):
        object_name = self.__upload_file_for_processing(index_entities_file, 'Index')

        files_to_upload, total_files_to_upload = self.__process_index(object_name, isolation_token)

        return files_to_upload, total_files_to_upload

    def upload_and_update_metadata(self, file_obj, isolation_token=None):
        object_name = self.__upload_file_for_processing(file_obj, 'Metadata')

        def add_data():
            return self.__repo.metadata.add_data_using_url('gs://' + object_name, isolation_token)

        status_with_timing('Server process metadata', add_data)

    def __append_index_file(self, file_info, combined_index_files):
        file_name = file_info['path']

        mtime = file_info['mtime']
        ctime = file_info.get('ctime', mtime)

        mtime = (mtime - epoch).total_seconds()
        ctime = (ctime - epoch).total_seconds()

        if file_info['sys'] == 'local':
            rel_path = os.path.relpath(file_name, self.__repo.data_path)

        else:  # file_info['sys'] == 's3':
            rel_path = file_name

        params = {
            'ctime': ctime,
            'mtime': mtime,
            'size': file_info['size'],
            'sha': file_info['sha'],
            'mode': 0
        }

        if 'url' in file_info:
            params['url'] = file_info['url']

        multi_line_json_from_data({rel_path: params}, combined_index_files, key_name='name')

    def __create_combined_index_and_metadata(self, data_path):
        import humanize
        status_line = PrintStatus()

        def on_result(result):
            data_files_info, metadata_files_list = result

            total_files_size = sum(x['size'] for x in data_files_info.values())

            status_line.print_status(
                'Total files {:,} ({}) (metadata found: {:,})', len(data_files_info),
                humanize.naturalsize(total_files_size), len(metadata_files_list))

        @disk_result(self.resume_token, '__create_combined_index_and_metadata', on_result)
        def with_disk_result():
            total_files = 0
            total_files_size = 0
            total_metadata = 0

            data_files_list = set()
            metadata_files_list = set()
            data_files_info = {}

            with closing(status_line):
                for file_info in enumerate_paths_with_info(data_path):
                    rel_file_name = self.repo.rel_path(file_info['path'])
                    total_files_size += file_info['size']

                    if rel_file_name.endswith(MetadataFiles.metadata_ext):
                        total_metadata += 1
                        metadata_files_list.add(rel_file_name)
                    else:
                        total_files += 1
                        data_files_list.add(rel_file_name)
                        data_files_info[rel_file_name] = file_info

                    status_line.print_status(
                        'Total files {:,} ({}) (metadata found: {:,})', total_files,
                        humanize.naturalsize(total_files_size), total_metadata)

            return data_files_info, metadata_files_list

        return with_disk_result()

    def create_combined_index_and_metadata(self, data_path):
        @disk_result(self.resume_token, 'create_combined_index_and_metadata')
        def with_disk_result():
            data_files_info, metadata_files_list = self.__create_combined_index_and_metadata(data_path)

            files_metadata = MetadataFiles.load_all_metadata(
                self.__repo, data_files_info, metadata_files_list, self.__no_progressbar)

            return files_metadata, data_files_info

        return with_disk_result()

    @wrap_exceptions
    def upload_in_batches(self, files_info, total_files=None, callback=None, isolation_token=None):
        total_files = total_files or len(files_info)
        batch_size = max(min(total_files // 100, 250), 250)  # FIXME: hardcoded

        for files_info_batch in get_batch_of_files_from_paths(files_info, batch_size):
            self.__repo.stage(files_info_batch, callback=callback, isolation_token=isolation_token)

    def download_all(self, query, root_folder, dest_pattern, batch_size, processes, save_meta=True):
        multi_process_control = get_multi_process_control(processes)
        return self.__download_all(multi_process_control, query, root_folder, dest_pattern, batch_size, save_meta=save_meta)

    def __download_normalized_item(self, process_control, storage, normalized_item, callback=None):
        volume_id = self.__repo.data_volume_config.volume_id

        def wrap_callback_func(current_item):
            def wrapper(_):
                if callback is not None:
                    callback(current_item)

            return wrapper

        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        config_init_dict = self.__ctx.obj.config.init_dict
        storage_params = storage.storage_params
        storage_params['class'] = fullname(storage)
        config_init_dict['storage'] = storage_params

        return process_control.execute(
            _download_entity,
            args=(config_init_dict, volume_id, normalized_item, self.__ctx.obj.session.headers),
            callback=wrap_callback_func(normalized_item))

    class DownloadIterResults(collections.Iterator):
        def __init__(self, repo, query, batch_size, silent=False):
            self.__query = query

            self.__batch_size = batch_size
            self.__repo = repo
            self.__query_offset = 0
            self.__total_data_points = None
            self.__current_iter = None
            self.__async = batch_size == -1
            self.__silent = silent

            if (self.__batch_size or 0) < 0:
                self.__batch_size = None

        def __get_next_results(self):
            def do_query():
                query_offset = None if not self.__query_offset else self.__query_offset
                return self.__repo.metadata.query(self.__query, async=self.__async, max_results=self.__batch_size, start_index=query_offset)

            if self.__async and not self.__silent:
                def on_summery_data(results):
                    import humanize
                    _, query_current_total_data_points, query_total_size = results

                    return '%s, %s Rows' % (humanize.naturalsize(query_total_size), humanize.intcomma(query_current_total_data_points))

                current_results, current_total_data_points, total_size = status_with_timing('Execute Query', do_query, fp=sys.stderr, on_summery_data=on_summery_data)
            else:
                current_results, current_total_data_points, total_size = do_query()

            def iter_items():
                next_results = current_results
                while True:
                    has_items = False
                    for metadata in next_results:
                        self.__query_offset += 1
                        has_items = True
                        yield normalize_item(metadata)

                    # in async mode we download everything in one pass
                    if self.__async or not has_items:
                        break

                    next_results, _, _ = do_query()

            return iter_items(), current_total_data_points, total_size

        def __len__(self):
            self.__prepare_iter_if_needed()

            return self.__total_data_points

        def __prepare_iter_if_needed(self):
            if self.__current_iter is not None:
                return

            results_iter, self.__total_data_points, total_size = self.__get_next_results()
            self.__current_iter = results_iter

        def __next__(self):
            self.__prepare_iter_if_needed()

            return next(self.__current_iter)

        next = __next__

        def __iter__(self):
            self.__prepare_iter_if_needed()
            return self

    def create_download_iter(self, query, batch_size=None, silent=False):
        return self.DownloadIterResults(self.__repo, query, batch_size, silent)

    def download_items(self, normalized_metadata_items, storage, multi_process_control):
        if len(normalized_metadata_items) == 0:
            return

        futures = []
        for normalized_item in normalized_metadata_items:
            async_result = self.__download_normalized_item(multi_process_control, storage, normalized_item)
            futures.append((async_result, normalized_item))

        for async_result, normalized_item in futures:
            async_result.wait()

    def __download_all(self, multi_process_control, query, root_folder, dest_pattern, batch_size, save_meta=True):
        from tqdm import tqdm

        def handle_item(item):
            file_name = DestPathEnum.get_full_path(dest_pattern, item)
            rel_path = os.path.relpath(file_name, root_folder)
            phase = item.get('phase', 'all')
            phase_meta.setdefault(phase, {})[rel_path] = item

            bar.update()

        download_iter = self.create_download_iter(query, batch_size)

        phase_meta = {}

        def get_next_results():
            try:
                return next(download_iter)
            except StopIteration:
                return None

        normalized_item = get_next_results()

        storage = DiskStorage(dest_pattern, save_meta)

        with tqdm(total=len(download_iter), desc="Downloading", unit=' data point', ncols=80, disable=self.__no_progressbar) as bar:
            with closing(multi_process_control):
                try:
                    while normalized_item is not None:
                        self.__download_normalized_item(multi_process_control, storage, normalized_item, handle_item)

                        normalized_item = get_next_results()
                except MetadataOperationError as ex:
                    eprint(str(ex))
                except KeyboardInterrupt:
                    multi_process_control.terminate()

        return phase_meta

    def save_metadata(self, root_dest, metadata):
        from tqdm import tqdm

        with tqdm(total=len(metadata), desc="saving metadata", unit=' files', ncols=80, disable=self.__no_progressbar) as bar:
            for key, val in metadata.items():
                if key is None:
                    key = 'unknown'

                json_metadata_file = os.path.join(root_dest, key + '.metadata.json')

                with open(json_metadata_file, 'w') as f:
                    json.dump(val, f)

                bar.update()

    def create_index_file_from_data(self, f, files_info):
        for val in files_info.values():
            self.__append_index_file(val, f)

    @classmethod
    def create_metadata_file_from_data(cls, f, metadata_files):
        dict_normalize(metadata_files)

        for rel_file_name, file_metadata in metadata_files.items():
            multi_line_json_from_data({rel_file_name: file_metadata}, f)

    def __get_files_to_upload(self, files_info, combined_index_files, isolation_token):
        files_to_upload, total_files_to_upload = self.upload_and_update_index(combined_index_files, isolation_token)

        def switch_to_full_path(params):
            rel_path = params['path']

            params['path'] = self.repo.full_path(rel_path)

            return params

        def enum_file_names():
            for file_name in files_to_upload:
                file_name = file_name.strip()

                yield file_name

        files_to_upload = [switch_to_full_path(files_info[rel_file_name]) for rel_file_name in enum_file_names()]

        return files_to_upload

    def __upload_full_index(self, index_entities_file, isolation_token):
        object_name = self.__upload_file_for_processing(index_entities_file, 'Index')
        index = self.__repo.open_index()

        def set_entries():
            return index.set_entries('gs://' + object_name, isolation_token)

        status_with_timing('Server process index', set_entries)

    def upload_index_and_metadata(self, data_path, isolation_token=None):
        def with_disk_result():
            metadata_files, files_info = self.create_combined_index_and_metadata(data_path)

            if len(files_info) == 0:
                return []

            if len(metadata_files) > 0:
                combined_meta_files = tempfile.TemporaryFile('wb+')
                self.create_metadata_file_from_data(combined_meta_files, metadata_files)
                self.upload_and_update_metadata(combined_meta_files, isolation_token)

            combined_index_files = tempfile.TemporaryFile('wb+')
            self.create_index_file_from_data(combined_index_files, files_info)

            if self.repo.data_volume_config.embedded:
                return self.__get_files_to_upload(files_info, combined_index_files, isolation_token)

            return self.__upload_full_index(combined_index_files, isolation_token)

        return with_disk_result()

    @classmethod
    def generate_resume_token(cls):
        size = 6
        chars = string.digits
        result = ''.join(random.choice(chars) for _ in range(size))

        return result
