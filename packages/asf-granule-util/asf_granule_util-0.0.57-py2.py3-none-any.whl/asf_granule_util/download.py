import requests
import json
import tqdm
import math
import os
import zipfile as zf
import contextlib

from .exceptions import (
    InvalidGranuleException,
    InvalidCredentialsException,
    GranuleDownloadException,
    NoGranulesFoundException
)
from .granules import SentinelGranule
from .pairs import SentinelGranulePair


def download(
        to_download,
        credentials,
        directory='.',
        progress_bar=False,
        unzip=True
):
    """Download sentinel granules or granule pairs from asf api

    :param to_download: granule string, SentinelGranule, or SentinelGranulePair
    :param credentials: dictionary containing the callers earthdata credentials
    :param directory: the directory where the granule will be downloaded
    :param progress_bar: show a progress_bar when downloading
    :param unzip: select if the granule should be unziped after downloading

    The credentials dictionary should look like:

    .. code-block:: python

       {'username': USERNAME, 'password': PASSWORD}

    """
    def make_dl_func_with_params(gran):
        return lambda: single_granule_download(
            gran,
            credentials,
            directory,
            progress_bar,
            unzip
        )

    if is_single_download(to_download):
        download_func = make_dl_func_with_params(to_download)
        download_func()

    elif isinstance(to_download, SentinelGranulePair):
        for g in to_download.tuple:
            download_func = make_dl_func_with_params(g)
            download_func()
    else:
        raise TypeError('Cannot download {}'.format(type(to_download)))


def is_single_download(to_download):
    try:
        # python2
        return isinstance(to_download, (SentinelGranule, str, unicode))
    except NameError:
        # python3
        return isinstance(to_download, (SentinelGranule, str))


def single_granule_download(
    granule,
    credentials,
    directory,
    progress_bar,
    unzip
):
    granule_str = str(granule)

    if not SentinelGranule.is_valid(granule_str):
        raise InvalidGranuleException(
            'Cannot download granule because it is not a sentinal granule.',
            granule_str
        )

    zip_url = get_download_url(granule_str)
    download_redirect = requests.get(zip_url)

    username, password = [credentials[k] for k in ['username', 'password']]
    dl_request = requests.get(
        download_redirect.url,
        auth=(username, password),
        stream=True
    )

    total_size = int(dl_request.headers.get('content-length', 0))
    download = get_download_stream(
        dl_request,
        progress_bar,
        total_size
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    granule_path = get_granule_path(directory, granule_str)
    do_download(download, granule_path, total_size)

    if not download_was_authorized(granule_path):
        raise InvalidCredentialsException('username or password incorrect')

    if unzip:
        do_unzip(granule_path)


def get_download_url(granule_str):
    api_url = 'https://api.daac.asf.alaska.edu/services/search/param'

    resp = requests.post(api_url, {
        'granule_list': granule_str,
        'output': 'JSON'
    })

    responses = json.loads(resp.text)[0]
    urls = [resp['downloadUrl'] for resp in responses]

    zip_urls = [url for url in urls if url.endswith('.zip')]

    if not zip_urls:
        raise NoGranulesFoundException(
            'no granules found with name: {}'.format(granule_str)
        )

    return zip_urls.pop()


def get_download_stream(dl_response, progress_bar, total_size):
    block_size = 1024

    if not progress_bar:
        download = dl_response.iter_content(block_size)
    else:
        download = tqdm.tqdm(
            dl_response.iter_content(block_size),
            total=math.ceil(total_size//block_size),
            unit='B',
            unit_scale=True
        )

    return download


def get_granule_path(directory, granule_str):
    granule_zip = granule_str + '.zip'

    return os.path.join(directory, granule_zip)


def do_download(download, directory, total_size):
    with open(directory, 'wb') as f:
        wrote = stream_to_file(f, download)

    if total_size != 0 and wrote != total_size:
        raise GranuleDownloadException("ERROR downloading granule")


def stream_to_file(f, download):
    wrote = 0
    for chunk in download:
        wrote += len(chunk)
        f.write(chunk)

    return wrote


def download_was_authorized(granule_path):
    return zf.is_zipfile(granule_path)


def do_unzip(path):
    output_path = os.path.dirname(path)

    with zipfile(path) as zf:
        zf.extractall(output_path)


@contextlib.contextmanager
def zipfile(path):
    zip_ref = zf.ZipFile(path, 'r')
    yield zip_ref
    zip_ref.close()
