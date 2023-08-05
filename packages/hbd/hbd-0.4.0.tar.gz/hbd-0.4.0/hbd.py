"""API to interface with Humble Bundle servers."""
# TODO: Download asmjs?

import csv
import hashlib
import json
import logging
from pathlib import Path, PurePath
from typing import Dict, List, Mapping, Optional

import attr
import requests


__version__ = '0.4.0'

HUMBLE_API_ROOT = 'https://www.humblebundle.com/api/v1'
HUMBLE_LOGIN_URL = 'https://www.humblebundle.com/processlogin'
HUMBLE_ORDERS_URL = f'{HUMBLE_API_ROOT}/user/order'
DOWNLOAD_CHUNK_SIZE = 1024 * 4

logger = logging.getLogger(__name__)


# Data structure definitions
#############################


class StructureCommon:
    """Methods common to all data structure classes."""
    @classmethod
    def create_filtered(cls, **kwargs):
        """Creates new class instance with unknown fields ignored.

        Used to prevent crash if nonbreaking fields are added to HB's API.
        """
        # TODO: Debugging flag to not ignore unknown fields
        fields = [f.name for f in attr.fields(cls)]  # pylint: disable=not-an-iterable
        filtered_args = {k: v for k, v in kwargs.items() if k in fields}
        return cls(**filtered_args)


# TODO: Considure data classes when Python 3.7 is released
@attr.s(auto_attribs=True, slots=True, frozen=True)
class Product(StructureCommon):
    """Data structure for product JSON."""
    automated_empty_tpkds: dict
    category: str
    human_name: str
    machine_name: str
    partial_gift_enabled: bool
    post_purchase_text: str
    supports_canonical: bool
    # Optional fields
    subscription_credits: Optional[int] = None
    # Parent
    _purchase: Optional['Purchase'] = None


@attr.s(auto_attribs=True, slots=True, frozen=True)
class DownloadStructUrl(StructureCommon):
    """Data structure for download_struct's urls JSON."""
    web: str
    # Optional fields
    bittorrent: Optional[str] = None
    # Parent
    _download_struct: Optional['DownloadStruct'] = None


@attr.s(auto_attribs=True, slots=True, frozen=True)
class DownloadStruct(StructureCommon):
    """Data structure for download_struct JSON."""
    human_size: str
    # Optional fields
    arch: Optional[str] = None
    asm_config: Optional[dict] = None
    asm_manifest: Optional[dict] = None
    external_link: Optional[str] = None
    file_size: Optional[int] = None
    force_download: Optional[bool] = None  # noqa
    hd_stream_url: Optional[str] = None
    kindle_friendly: Optional[bool] = None
    md5: Optional[str] = None
    name: Optional[str] = None
    sd_stream_url: Optional[str] = None
    sha1: Optional[str] = None
    small: Optional[int] = None
    timestamp: Optional[int] = None
    uploaded_at: Optional[str] = None
    url: Optional[DownloadStructUrl] = None
    uses_kindle_sender: Optional[bool] = None
    # Parent
    _download: Optional['Download'] = None

    @property
    def file_name(self) -> str:
        """Extract the file name from the URL."""
        if self.url:
            return self.url.web.split('/')[-1].split('?', 1)[0]
        else:
            raise ValueError('No downloads available for this struct')


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Download(StructureCommon):
    """Data structure for download JSON."""
    android_app_only: bool
    download_identifier: str
    download_struct: List[DownloadStruct]
    download_version_number: str
    machine_name: str
    options_dict: dict
    platform: str
    # Parent
    _subproduct: Optional['Subproduct'] = None


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Subproduct(StructureCommon):
    """Data structure for subproduct JSON."""
    custom_download_page_box_html: str
    downloads: List[Download]
    human_name: str
    icon: str
    machine_name: str
    library_family_name: str
    payee: dict
    url: str
    # Parent
    _purchase: Optional['Purchase'] = None


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Purchase(StructureCommon):
    """Data structure for purchase JSON."""
    amount_spent: int
    claimed: bool
    created: str
    currency: str
    gamekey: str
    is_giftee: bool
    missed_credit: None
    path_ids: list
    product: Product
    subproducts: List[Subproduct]
    total: int
    uid: str
    # Optional fields
    all_coupon_data: Optional[list] = None

    @classmethod
    def convert_purchase_data(cls, purchase_data: Mapping) -> 'Purchase':
        """Convert JSON to internal data structures."""
        # NOTE: Shallow copy, maybe do deep copy in future
        new_data = dict(purchase_data)
        new_data['product'] = Product.create_filtered(**purchase_data['product'])
        fixed_subproducts = []
        for subproduct in purchase_data['subproducts']:
            fixed_downloads = []
            for download in subproduct['downloads']:
                fixed_structs = []
                for struct in download['download_struct']:
                    # Some download_structs have no downloads (e.g. streaming)
                    if 'url' in struct:
                        fixed_download_urls = DownloadStructUrl.create_filtered(**struct['url'])
                        struct['url'] = fixed_download_urls
                    # At least one bundle has this typo (androidbundle4)
                    if 'timetstamp' in struct:
                        struct['timestamp'] = struct['timetstamp']
                        del struct['timetstamp']
                    # At least one bundle has this typo (hib14)
                    if 'timestmap' in struct:
                        # It already has a timestamp field with a higher value
                        # so I guess just ditch the old one?
                        del struct['timestmap']
                    # At least one bundle has this typo (booktrope_bookbundle)
                    if 'kindle-friendly' in struct:
                        struct['kindle_friendly'] = struct['kindle-friendly']
                        del struct['kindle-friendly']
                    fixed_struct = DownloadStruct.create_filtered(**struct)
                    fixed_structs.append(fixed_struct)
                download['download_struct'] = fixed_structs
                fixed_downloads.append(download)
            subproduct['downloads'] = list(map(
                lambda d: Download.create_filtered(**d), fixed_downloads))
            fixed_subproducts.append(subproduct)
        new_data['subproducts'] = list(map(
            lambda s: Subproduct.create_filtered(**s), fixed_subproducts))

        purchase = cls.create_filtered(**new_data)
        # Insert parentage info
        # Objects are frozen, use object.__setattr__ to bypass
        object.__setattr__(purchase.product, '_purchase', purchase)
        for subproduct in purchase.subproducts:
            for download in subproduct.downloads:
                for struct in download.download_struct:
                    object.__setattr__(struct, '_download', download)
                    if struct.url:
                        object.__setattr__(struct.url, '_download_struct', struct)
                object.__setattr__(download, '_subproduct', subproduct)
            object.__setattr__(subproduct, '_purchase', purchase)

        return purchase

    def find_downloads(self, output_format: str = '{FileName}') \
            -> Dict[Path, DownloadStruct]:
        """Extracts all possible downloads from a Purchase."""
        # TODO: Filters for platform, type, etc.
        downloads = {}
        for subproduct in self.subproducts:
            for subdownload in subproduct.downloads:
                # asmjs platform has no downloads (officially)
                if subdownload.platform != 'asmjs':
                    for download_struct in subdownload.download_struct:
                        path_vars = self._create_path_vars(
                            subproduct, subdownload, download_struct)
                        output_path = Path(output_format.format(**path_vars))
                        downloads[output_path] = download_struct
        return downloads

    def _create_path_vars(self,
                          subproduct: Subproduct,
                          download: Download,
                          download_struct: DownloadStruct) -> Dict[str, str]:
        """Create a dict containing values used for output path formatting."""
        return {
            'FileName': download_struct.file_name,
            'MachineName': download.machine_name,
            'Platform': Download.platform,
            'ProductCategory': self.product.machine_name,
            'ProductHumanName': self.product.machine_name,
            'ProductHumanNameClean': remove_the(self.product.machine_name),
            'ProductHumanNameThe': move_the(self.product.machine_name),
            'ProductMachineName': self.product.machine_name,
            'PurchaseDate': self.created,
            'SubproductHumanName': subproduct.human_name,
            'SubproductHumanNameClean': remove_the(subproduct.human_name),
            'SubproductHumanNameThe': move_the(subproduct.human_name),
            'SubproductMachineName': subproduct.machine_name
        }

    @property
    def total_size(self) -> int:
        """Calculate total size of all downloads."""
        return sum(v.file_size for v in self.find_downloads().values())


# Exceptions
#############

class HumbleError(Exception):
    """Base class for all exceptions raised by this module."""
    pass


class HumbleCacheError(HumbleError):
    """Error reading or writing a cache file."""
    pass


class HumbleConnectionError(HumbleError):
    """Error getting data from Humble Bundle's servers."""
    pass


# Main interface
#################

class HumbleDownloader:
    """API interface for Humble Bundle purchases."""
    def __init__(self,
                 session_key: Optional[str] = None,
                 cache_dir: Optional[Path] = None) -> None:
        self.session = requests.Session()
        # No official API, we're pretending to be the Android app
        self.session.headers.update({
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "Keep-Alive": "true",
            "X-Requested-By": "hb_android_app",
            "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)"
        })
        if session_key:
            self.set_session(session_key)

        self.cache_dir = cache_dir
        if cache_dir:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                cache_dir.joinpath('orders').mkdir(exist_ok=True)
            except OSError:
                logger.warning(f"Cannot write to cache directory {cache_dir}, caching disabled")
                self.cache_dir = None

    def login(self, username: str, password: str):
        """Authenticate with Humble API."""
        # NOTE: NOT CURRENTLY WORKING
        # TODO: Figure out how to handle CAPTCHA and fix this method
        login_details = {'username': username, 'password': password}
        self.session.post(HUMBLE_LOGIN_URL, data=login_details,
                          params={"ajax": "true"})

    def set_session(self, session_key: str):
        """Set the session key to use."""
        self.session.cookies['_simpleauth_sess'] = session_key

    def get_purchase_list(self) -> List[str]:
        """Get all purchase keys from Humble Bundle."""
        try:
            request = self.session.get(HUMBLE_ORDERS_URL)
            return [k['gamekey'] for k in request.json()]
        except requests.exceptions.ConnectionError as exc:
            message = "Unable to connect to Humble Bundle"
            logger.exception(message)
            raise HumbleConnectionError(message) from exc
        except json.decoder.JSONDecodeError as exc:
            # TODO: test this handler
            message = "Invalid JSON data from Humble Bundle"
            logger.exception(message)
            raise HumbleConnectionError(message) from exc

    def get_purchase(self, key: str) -> Purchase:
        """Retrieve data on a specific purchase.

        Will load data from cache if present. If this is not desired, disable
        the cache or use clear_purchase_cache() before calling this method.
        """

        # Load from cache if possible
        purchase_data = None
        try:
            purchase_data = self._load_purchase_json_cache(key)
        except HumbleCacheError:
            logger.warning("Failure loading cache, downloading from Humble")

        # If the cache didn't work download it from Humble servers
        if not purchase_data:
            # Note this will raise a HumbleConnectionError on failure
            purchase_data = self._load_purchase_json_download(key)

        return Purchase.convert_purchase_data(purchase_data)

    def clear_purchase_cache(self, key: str):
        """Remove cached data for a purchase."""
        if self.cache_dir:
            cache_path = self._create_order_cache_path(key)
            try:
                cache_path.unlink()
            except OSError as exc:
                message = f"Unable to delete purchase cache file {cache_path}"
                logger.exception(message)
                raise HumbleCacheError(message) from exc

    def _load_purchase_json_cache(self, key: str):
        """Get JSON for purchase from cache if available.

        Returns `None` on cache miss.
        """
        json_cache_file = self._create_order_cache_path(key)
        purchase_data = None
        if self.cache_dir and json_cache_file.exists():
            logger.info(f'Loading purchase {key} from local cache')
            try:
                with json_cache_file.open() as order_file:
                    purchase_data = json.load(order_file)
            except OSError as exc:
                message = f"Unable to load cached purchase from {json_cache_file}"
                logger.warning(message)
                raise HumbleCacheError(message) from exc
            except json.decoder.JSONDecodeError as exc:
                message = f"Purchase cache {json_cache_file} corrupt, purging"
                logger.warning(message)
                try:
                    json_cache_file.unlink()
                except OSError:
                    logger.warning(f"Unable to delete file {json_cache_file}")
                raise HumbleCacheError(message) from exc
        return purchase_data

    def _load_purchase_json_download(self, key: str):
        """Get JSON for purchase from Humble servers"""
        logger.info(f'Loading purchase {key} from Humble Bundle')
        try:
            request = self.session.get(f'{HUMBLE_API_ROOT}/order/{key}')
            purchase_data = request.json()
            # Cache purchase JSON
            if self.cache_dir:
                json_cache_path = self._create_order_cache_path(key)
                with json_cache_path.open('w') as cache_file:
                    cache_file.write(request.text)
        except requests.exceptions.ConnectionError as exc:
            message = "Unable to connect to Humble Bundle"
            logger.exception(message)
            raise HumbleConnectionError(message) from exc
        except json.decoder.JSONDecodeError as exc:
            message = f"Invalid JSON data from purchase {key}"
            # TODO: test this handler
            logger.exception(message)
            raise HumbleConnectionError(message) from exc
        except OSError:
            logger.warning(f'Unable to write cache file {json_cache_path}')

        return purchase_data

    def _create_order_cache_path(self, key: str) -> Path:
        """Generate a path to store order JSON cache data.

        If a cache dire has not been set, use NullPath to return a virtual
        path object.
        """
        filename = key + '.json'
        # Generate a fake path if caching disabled
        if not self.cache_dir:
            return NullPath('NULLPATH') / filename
        return self.cache_dir / 'orders' / filename

    def find_key_from_name(self, machine_name: str) -> Optional[str]:
        """Givin a machine name, search the bundles for its key."""
        if self.cache_dir:
            try:
                keynames = self._load_keyname_cache()
            except HumbleCacheError:
                logger.warning('Cannot load keyname cache, loading from Humble')
                keynames = {}
        else:
            logger.info("Cache disabled, loading keynames from Humble")
            keynames = {}

        if machine_name in keynames:
            key = keynames[machine_name]
            logger.info(f"Machine name found, {machine_name} has key {key}")
            return key

        logger.info("Name not already cached, searching purchases")
        keys = self.get_purchase_list()
        machine_name_key = None
        for key in keys:
            purchase = self.get_purchase(key)
            keynames[purchase.product.machine_name] = key
            if purchase.product.machine_name == machine_name:
                machine_name_key = key
                break

        if self.cache_dir:
            try:
                self._save_keyname_cache(keynames)
            except HumbleCacheError:
                logger.warning("Unable to save keyname cache")
        return machine_name_key

    def _load_keyname_cache(self) -> Dict[str, str]:
        """Load keynames from CSV cache file."""
        keyname_cache = self.cache_dir / 'keynames.csv'
        logger.info(f"Loading keyname cache from {keyname_cache}")
        keynames: dict = {}
        if keyname_cache.exists():
            try:
                with keyname_cache.open(newline='') as csvfile:
                    keyname_dicts = list(csv.DictReader(csvfile))
                    keynames = {key_dict['machine_name']: key_dict['key'] for
                                key_dict in keyname_dicts}
            except (OSError) as exc:
                message = f"Unable to read keyname cache file {keyname_cache}"
                logger.exception(message)
                raise HumbleCacheError(message) from exc
            except (csv.Error) as exc:
                message = f"Keyname cache file {keyname_cache} is corrupt"
                logger.exception(message)
                raise HumbleCacheError(message) from exc
        return keynames

    def _save_keyname_cache(self, keynames: Mapping):
        """Write out keynames to a CSV cache file."""
        keyname_cache = self.cache_dir / 'keynames.csv'
        logger.info(f"Saving keyname cache to {keyname_cache}")
        try:
            with keyname_cache.open('w', newline='') as csvfile:
                keyname_writer = csv.DictWriter(csvfile,
                                                ('machine_name', 'key'))
                keyname_pairs = [{'machine_name': n, 'key': k} for n, k in
                                 keynames.items()]
                keyname_writer.writeheader()
                keyname_writer.writerows(keyname_pairs)
        except (OSError, csv.Error) as exc:
            message = f"Unable to write keyname cache file {keyname_cache}"
            logger.exception(message)
            raise HumbleCacheError(message) from exc


# Utility functions
####################

def download_file(url: str,
                  output_path: Path,
                  progress_callback=lambda _: None):
    """Download file described by a download_struct to disk."""
    request_stream = requests.get(url, stream=True)
    with output_path.open('wb') as f:
        # Zero length means the download URL has expired
        if request_stream.headers['Content-Length'] == '0':
            raise EOFError('Download URL expired')
        # TODO: Error handling for this
        for chunk in request_stream.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            # Filter keep-alive packets
            if chunk:
                f.write(chunk)
                progress_callback(len(chunk))


def verify_download(download_struct: DownloadStruct,
                    path: Path) -> bool:
    """Use the information in the download stuct to check file path."""
    # Check file size
    file_size = path.lstat().st_size
    if file_size != download_struct.file_size:
        return False

    # File is correct size, so let's check contents
    # Using MD5 as not all downloads have a SHA1 available
    file_hash = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(file_hash.block_size * 32), b''):
            file_hash.update(chunk)
    return file_hash.hexdigest() == download_struct.md5


def remove_the(the_text: str) -> str:
    """Converts 'The Title' text to 'Title'."""
    return the_text[4:] if the_text.startswith("The ") else the_text


def move_the(the_text: str) -> str:
    """Converts 'The Title' text to 'Title, The'."""
    return the_text[4:] + ', The' if the_text.startswith("The ") else the_text


# TODO: implement remaining Path methods
# Ugly hack to allow subclassing Path/PurePath
# https://stackoverflow.com/a/34116756
class NullPath(type(PurePath())):  # type: ignore
    """Emulates a Path object that does not perform filesystem operations."""

    @staticmethod
    def exists() -> bool:
        """Null paths do not exist, always return False."""
        return False
