import yaml
import logging
import os

from dli.client.s3 import Client, S3DatasetWrapper
from dli.client.s3_token_refresher import make_s3_token_refresher
from dli.siren import siren_to_entity, siren_to_dict

from dli.client.exceptions import PackageNotFoundException, DatasetNotFoundException, DownloadFailed

logger = logging.getLogger(__name__)


def to_dict(o, remove_fields=None):
    import inspect
    if remove_fields is None:
        remove_fields = []
    return {
        f: getattr(o, f)
        for f in o.__class__.__dict__.keys()
        if f not in remove_fields and
            not f.startswith('_') and
            hasattr(o, f) and
            not inspect.ismethod(getattr(o, f))
    }


class DatasetFunctions(object):

    def register_dataset_metadata(
        self,
        package_id,
        description,
        files,
        version=1,
        format='csv',
        keywords=None,
        tags=None,
        sources=None
    ):
        """
        Convenience method to register metadata and create a new dataset.
        This function WILL NOT upload files

        :param package_id: The id of the package this dataset belongs to. Can
                 be provided in dataset definition
        :type package_id: str
        :param description: Description of the dataset
        :type description: str
        :param files: Path of the files or folders to register
        :type files: list[str]
        :param version: Version for this dataset, ``1`` by default
        :type version: int
        :param format: Format for this dataset, ``csv`` by default.
        :type format: str
        :param keywords: Keywords to be associated with the dataset.
        :type keywords: list[str]
        :param tags: Tags to be associated with the dataset
        :type tags: dict[str, str]
        :param sources: Sources for lineage definition
        :type sources: list[str]

        :returns: The newly registered dataset
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dl.register_dataset_metadata(
                    package_id,
                    description="test",
                    files=["/path/to/file/A", "/path/to/file/B"]
                )
        """
        if not files:
            raise Exception("No files to register have been provided.")

        info = {
            'metadata': {
                'description': description,
                'format': format,
                'keywords': keywords or [],
                'tags': tags or {},
                'version': version,
                'lineage': {
                    'generatedBy': 'SDK upload',
                    'sources': sources or []
                },
                'files': files
            }
        }

        return self._register_dataset(info, package_id=package_id)

    def register_dataset(
        self,
        package_id,
        description,
        s3_prefix,
        files,
        version=1,
        format='csv',
        keywords=None,
        tags=None,
        sources=None
    ):
        """
        Convenience method to register metadata and create a new dataset.
        This function will perform an upload of the files to one
        of the supported data stores

        Supported data stores:
        - s3

        :param package_id: The id of the package this dataset belongs to. Can
                 be provided in dataset definition
        :type package_id: str
        :param description: Description of the dataset
        :type description: str
        :param s3_prefix: location for the files in the destination
        :type s3_prefix: str
        :param files: Path of the files or folders to register
        :type files: list[str]
        :param version: Version for this dataset, ``1`` by default
        :type version: int
        :param format: Format for this dataset, ``csv`` by default.
        :type format: str
        :param keywords: Keywords to be associated with the dataset.
        :type keywords: list[str]
        :param tags: Tags to be associated with the dataset
        :type tags: dict[str, str]
        :param sources: Sources for lineage definition
        :type sources: list[str]

        :returns: The newly registered dataset
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dl.register_dataset(
                    package_id=package.id,
                    description="My dataset",
                    s3_prefix="quotes/20180518/",
                    files=["./test_sandbox/samples/data/AAPL.csv", "./test_sandbox/samples/data/MSFT.csv"],
                    format="csv",
                    tags={
                        "business-date": "20180518",
                        "asset-class": "Equity",
                        "asset-type": "Common Stock",
                        "region": "US"
                    },
                    keywords=["APPLE", "MSFT"]
                )
        """
        if not files:
            raise Exception("No files to register have been provided.")

        info = {
            'metadata': {
                'description': description,
                'format': format,
                'keywords': keywords or [],
                'tags': tags or {},
                'version': version,
                'lineage': {
                    'generatedBy': 'SDK upload',
                    'sources': sources or []
                },
            },
            'uploads': [
                {
                    'files': files,
                    'target': {'s3': {'prefix': s3_prefix}}
                }
            ]
        }

        return self._register_dataset(info, package_id=package_id)

    def register_dataset_with_config_file(self, path, package_id=None):
        """
        Register a dataset using a YAML file which defines a dataset

        :param path: The path to a YAML file defining a dataset
        :type path: str
        :param package_id: The id of the package this dataset belongs to. Can
                 be provided in dataset definition
        :type package_id: str

        :returns: The newly registered dataset
        :rtype: collections.namedtuple
        """
        with open(path, 'r') as stream:
            try:
                info = yaml.load(stream)
                return self._register_dataset(info, package_id)
            except yaml.YAMLError as exc:
                logger.exception("Error: %s.", exc)

    def update_dataset_metadata(
        self,
        dataset_id,
        description=None,
        files=None,
        version=None,
        format=None,
        keywords=None,
        tags=None,
        sources=None
    ):
        """
        Update a dataset using the given metadata.
        This function will NOT upload files, it just as a means to ammend
        mistakes in a previously submitted dataset instance.

        All arguments are optional, meaning arguments passed as None will not be modified

        :param dataset_id: The id of the dataset to update
        :type dataset_id: str
        :param description: Description of the dataset
        :type description: str
        :param files: Path of the files to upload
        :type files: list[str]
        :param s3_prefix: The key under which the files will be stored in S3
        :type s3_prefix: str
        :param keywords: Keywords to be associated with the dataset.
        :type keywords: list[str]
        :param tags: Tags to be associated with the dataset
        :type tags: dict[str, str]

        :returns: The updated dataset
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dl.update_dataset_metadata(
                    dataset_id,
                    description="Fixed dataset",
                    version=2,
                    keywords=["AAPL", "MSFT"],
                    tags={
                        "business-date": "20180518",
                        "asset-class": "Equity",
                        "asset-type": "Common Stock",
                        "region": "US"
                    }
                )
        """
        info = {
            'description': description,
            'files': files,
            'format': format,
            'keywords': keywords,
            'tags': tags,
            'version': version
        }

        if sources:
            info['lineage'] = {
                'generatedBy': 'SDK upload',
                'sources': sources
            }

        info = {k: v for k, v in info.items() if v is not None}

        if not info:
            raise Exception("At least one value needs to be updated has to be provided ")

        return self._update_dataset(info, dataset_id=dataset_id)

    def _update_dataset(self, metadata, dataset_id=None):
        """
        Update a dataset using the given metadata

        :param metadata: A dict representing the updated dataset
        :type metadata: dict
        :param dataset_id: The id of the dataset to update
        :type dataset_id: str

        :returns: The updated dataset
        :rtype: collections.namedtuple
        """
        if not dataset_id:
            if "datasetId" in metadata:
                dataset_id = metadata["datasetId"]

        if not dataset_id:
            raise Exception("Dataset Id must be provided as a parameter, or as part of metadata")

        dataset = self._get_dataset(dataset_id)
        if not dataset:
            raise Exception("No dataset found with id %s" % dataset_id)

        dataset_as_dict = siren_to_dict(dataset)
        dataset_as_dict['datasetId'] = dataset_id
        if 'id' in dataset_as_dict:
            del dataset_as_dict['id']

        dataset_as_dict.update(metadata)
        dataset.update_dataset(__json=dataset_as_dict)
        return self.get_dataset(dataset_id)

    def _register_dataset(self, info, package_id=None):
        """
        Manually register a dataset

        :param info: A dictionary containing a `metadata` entry, which
                 specifies the dataset metadata, as well as an 'uploads' entry,
                 to specify the files which should be uploaded and recorded with
                 the metadata.
        :type info: dict
        :param package_id: The id of the package this dataset belongs to. Can
                 be provided in dataset definition
        :type package_id: str

        :returns: Registered dataset
        :rtype: collections.namedtuple
        """
        uploaded_files = []
        metadata = info['metadata']

        if not package_id:
            if "packageId" in metadata:
                package_id = metadata["packageId"]

        if not package_id:
            raise Exception("Package Id must be provided as a parameter, or as part of metadata")

        package = self._get_package(package_id)

        if hasattr(package, 'dataStorage'):
            if package.dataStorage == 'S3':
                if not hasattr(package, 's3Bucket'):
                    raise Exception("There is no bucket associated with the package {}".format(package.id))

                s3_bucket = package.s3Bucket

                if 'uploads' in info:
                    for upload in info['uploads']:
                        uploaded_files.append(self._process_upload(upload, package_id, s3_bucket))

                    metadata['files'] = [
                        item for sublist in uploaded_files for item in sublist
                    ]

        if not package:
            raise PackageNotFoundException(package_id)

        dataset = package.add_dataset(__json=metadata)
        return siren_to_entity(dataset)

    def delete_dataset(self, dataset_id):
        """
        Marks a dataset as deleted.

        :param dataset_id: the unique id for the dataset we want to delete.
        :type dataset_id: str

        :returns:

        - **Sample**

        .. code-block:: python

                dl.delete_dataset(dataset_id)
        """
        dataset = self._get_dataset(dataset_id)
        if not dataset:
            raise Exception("No dataset found with id: %s" % dataset_id)

        dataset.delete_dataset(dataset_id=dataset_id)

    def get_s3_dataset(self, dataset_id):
        """
        Fetches an S3 dataset providing easy access to directly
        stream/load files without the need of downloading them.

        If the dataset is not stored in S3, or you don't have access to it
        then an error will be displayed.

        :param str dataset_id: The id of the dataset we want to load

        :returns: a dataset that can read files from S3
        :rtype: dli.client.s3.S3DatasetWrapper

        .. code-block:: python

                dataset = client.get_s3_dataset(dataset_id)
                with dataset.open_file("path/to/file/in/dataset") as f:
                    f.read() # do something with the file
                    
                # or if you want a pandas dataframe created from it you can
                pd.read_csv(dataset.open_file("path/to/file/in/dataset"))

                # you can see all the files in the dataset by calling `files`
                dataset.files  # displays a list of files in this dataset

        """

        dataset = self.get_dataset(dataset_id)
        keys = self.get_s3_access_keys_for_package(dataset.packageId)
        s3_access = Client(
            keys['accessKeyId'],
            keys['secretAccessKey'],
            keys['sessionToken']
        )

        return S3DatasetWrapper(dataset._asdict(), s3_access.s3fs)

    def download_dataset(self, dataset_id, destination):
        """
        Helper function that downloads all files
        registered in a dataset into a given destination.

        This function is only supported for data-lake managed s3 buckets,
        otherwise an error will be displayed.

        Currently supports:
          - s3

        :param dataset_id: The id of the dataset we want to download files from
        :type dataset_id: str
        :param destination: Target location where to store the files (expected to be a directory)
        :type destination: str

        - **Sample**

        .. code-block:: python

                data = client.download_dataset(dataset.id, destination)
        """

        # get the s3 keys
        # this requires access to be granted
        dataset = self._get_dataset(dataset_id)
        if not dataset:
            raise DatasetNotFoundException("No dataset found with id %s" % dataset_id)

        keys = self.get_s3_access_keys_for_package(dataset.packageId)
        s3_access = Client(
            keys['accessKeyId'],
            keys['secretAccessKey'],
            keys['sessionToken']
        )

        # for each file/folder in the dataset, attempt to download the file
        # rather than failing at the same error, keep to download as much as possible
        # and fail at the end.
        failed = []
        files = [f["path"] for f in dataset.files]
        for file in files:
            try:
                s3_access.download_file(file, destination)
            except Exception:
                logger.exception("Failed to download file `%s` from dataset `%s`", file, dataset_id)
                failed.append(file)

        if failed:
            raise DownloadFailed(
                "Some files in this dataset could not be downloaded, "
                "see logs for detailed information. Failed:\n%s"
                % "\n".join(failed)
            )

    def _process_upload(self, upload, package_id, s3_bucket):
        """
        Given an `upload` dict spec, process the files by uploading them to
        the specified target

        Currently supports:
          - s3

        :param upload: A dictionary specifying an upload `target` dict and a
                 list of files to upload
                 Example:
                 {
                     'files': ['DrowningsPerYearVsNicolasCageMovies.csv']
                     'target': {
                         's3': {
                             'prefix': '/spurious-correlations/'
                         }
                     }
                 }

                 Files can also be expressed as an object like this:
                 {
                     'files': [{
                         'path': 'DrowningsPerYearVsNicolasCageMovies.csv',
                         'size': 100000
                     }]
                     'target': {
                         's3': {
                             'prefix': '/spurious-correlations/'
                         }
                     }
                 }

        :type upload: dict
        :param package_id: The id of the package this dataset belongs to. Can
                 be provided in dataset definition
        :type package_id: str
        :param s3_bucket: The name of the S3 bucket you wish to upload files to
        :type s3_bucket: str

        :returns: A list of paths of the uploaded files
        :rtype: list[str]
        """
        files = upload['files']
        target = upload['target']

        if 's3' in target:
            prefix = target['s3']['prefix']
            s3_location = '{}/{}'.format(s3_bucket, prefix)
            return self._process_s3_upload(files, s3_location, package_id)
        else:
            raise Exception("Only S3 uploads are currently supported")

    def _process_s3_upload(self, files, s3_location, package_id):
        s3_access_keys = self.get_s3_access_keys_for_package(package_id)
        token_refresher = make_s3_token_refresher(self, package_id)
        s3_client = Client(s3_access_keys['accessKeyId'], s3_access_keys['secretAccessKey'], s3_access_keys['sessionToken'])
        return s3_client.upload_files_to_s3(files, s3_location, token_refresher)

    def get_dataset(self, dataset_id):
        """
        Fetches dataset metadata for an existing dataset.

        :param dataset_id: the unique id for the dataset we want to fetch.
        :type dataset_id: str

        :returns: The dataset
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dataset = dl.get_dataset(dataset_id)
        """
        dataset = self._get_dataset(dataset_id)
        if not dataset:
            return

        return siren_to_entity(dataset)

    def _get_dataset(self, dataset_id):
        return self.get_root_siren().get_dataset(dataset_id=dataset_id)

    def add_files_to_dataset(self, dataset_id, s3_prefix, files):
        """
        Upload files to existing dataset

        :param dataset_id: The id of the dataset to be updated
        :type dataset_id: str
        :param s3_prefix: Location for the files in the destination s3 bucket
        :type s3_prefix: str
        :param files: List of files to be added to the dataset
        :type files: list[str]

        :returns: The updated dataset
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dl.add_files_to_dataset(
                  dataset_id=dataset.id,
                  s3_prefix="quotes/20180518/",
                  files=["./data/AAPL.csv", "./data/MSFT.csv"],
                )
        """
        dataset = self.get_dataset(dataset_id)
        if dataset:
            pkg = self.get_package(dataset.packageId)
            if pkg:
                s3_location = "{}/{}".format(pkg.s3Bucket, s3_prefix)
                uploaded_files = self._process_s3_upload(files, s3_location, pkg.id)

                if dataset.files:
                    uploaded_files.extend(dataset.files)

                metadata_update = {
                    'files': uploaded_files
                }

                return self._update_dataset(metadata_update, dataset_id)
            else:
                raise PackageNotFoundException(
                    message='Package {} associated with the dataset {} does not exist!'.format(
                        dataset.packageId,
                        dataset_id
                    )
                )
        else:
            raise DatasetNotFoundException(
                'Dataset with id {} not found'.format(dataset_id)
            )
