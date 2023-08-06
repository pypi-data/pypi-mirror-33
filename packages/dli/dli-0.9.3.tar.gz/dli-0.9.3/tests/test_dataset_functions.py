import logging
import os

import six

from backports import tempfile
from tests.common import SdkIntegrationTestCase, build_fake_s3fs
from unittest import skip
from mock import patch, call
from dli.client.exceptions import PackageNotFoundException, InvalidPayloadException, DatasetNotFoundException, DownloadFailed


logger = logging.getLogger(__name__)


class DatasetFunctionsTestCase(SdkIntegrationTestCase):

    def test_get_unknown_dataset_returns_none(self):
        self.assertIsNone(self.client.get_dataset("unknown"))

    def test_register_dataset_metadata(self):
        description = "test dataset"
        files = ["/path/to/file/A", "/path/to/file/B"]
        package_id = self.create_package_with_no_bucket(
            "test_register_dataset_metadata"
        )

        dataset = self.client.register_dataset_metadata(
            package_id,
            description,
            files
        )

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.packageId, package_id)
        self.assertEqual(dataset.description, description)
        self.assertEqual(dataset.files, list(map(lambda f: {"path": f}, files)))

    def test_register_dataset_metadata_fails_when_no_files_provided(self):
        package_id = self.create_package_with_no_bucket(
            "test_register_dataset_metadata_fails_when_no_files_provided"
        )

        with self.assertRaises(Exception):
            self.client.register_dataset_metadata(package_id, "desc", files=[])

    def test_update_dataset_fails_for_unknown_dataset(self):
        with self.assertRaises(Exception) as cm:
            self.client.update_dataset("unknown")
            self.assertEqual(cm.exception.message, "No dataset found with id unknown")

    def test_register_dataset_can_create_dataset_uploading_files(self):
        description = "test dataset"
        file = os.path.relpath(__file__)  # upload ourselves as a dataset
        package_id = self.create_package(
            "test_register_dataset_can_create_dataset_uploading_files"
        )

        dataset = self.client.register_dataset(
            package_id,
            description,
            "prefix/",
            [file]
        )

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.packageId, package_id)
        self.assertEqual(dataset.description, description)
        self.assertEqual(dataset.files, [
            {"path": "s3://local-ihsm-dl-pkg-test/prefix/" + os.path.basename(file)}
        ])

    def test_update_dataset_merges_changes_with_existing_dataset(self):
        package_id = self.create_package_with_no_bucket(
            "test_update_dataset_merges_changes_with_existing_dataset"
        )
        dataset = self.client.register_dataset_metadata(
            package_id,
            "test",
            ["/path/to/file/A", "/path/to/file/B"],
            tags={
                "business-date": "yesterday",
                "asset-class": "fixed-income"
            }
        )

        updated = self.client.update_dataset_metadata(
            dataset.id,
            description="correct desc."
        )

        self.assertEqual(dataset.id, updated.id)
        self.assertEqual(dataset.files, updated.files)
        self.assertEqual(updated.description, "correct desc.")
        self.assertEqual(dataset.tags, updated.tags)

    def test_can_delete_dataset(self):
        package_id = self.create_package_with_no_bucket(
            "test_can_delete_dataset"
        )
        dataset = self.client.register_dataset_metadata(
            package_id,
            "test",
            ["/path/to/file/A", "/path/to/file/B"]
        )
        # delete the dataset
        self.client.delete_dataset(dataset.id)
        # can't read it back
        self.assertIsNone(self.client.get_dataset(dataset.id))

    def test_delete_unknown_dataset_raises_exception(self):
        with self.assertRaises(Exception):
            self.client.delete_dataset("unknown")

    def test_can_add_files_to_existing_dataset(self):
        description = "test dataset"
        file = os.path.relpath(__file__)  # upload ourselves as a dataset
        package_id = self.create_package(
            "test_can_add_files_to_existing_dataset"
        )

        dataset = self.client.register_dataset(
            package_id,
            description,
            "prefix/",
            [file]
        )
        file2 = '../test_sandbox/samples/data/AAPL.csv'
        dataset_updated = self.client.add_files_to_dataset(dataset.id, 'prefix/', [file2])

        # countEqual asserts that the collections match disrespect of order
        # talk about naming stuff
        six.assertCountEqual(
            self,
            [ 
                {"path": "s3://local-ihsm-dl-pkg-test/prefix/" + os.path.basename(file)},
                {"path": "s3://local-ihsm-dl-pkg-test/prefix/" + os.path.basename(file2)}
            ],
            dataset_updated.files
        )

        self.assertEqual(dataset_updated.description, description)  # DL-508

    def test_add_files_to_unknown_dataset_raises_exception(self):
        with self.assertRaises(DatasetNotFoundException):
            self.client.add_files_to_dataset('unknown', 'prefix', ["/path/to/file/A"])

    def test_register_dataset_to_nonexisting_pacakge(self):
        with self.assertRaises(PackageNotFoundException) as context:
            ds = self.client.register_dataset(package_id='12345',
                                              description="new dataset api",
                                              s3_prefix="auto_test/20180511/",
                                              files=["./data/total_production_per_field - 1.csv", "./data/info.txt"],
                                              version=3,
                                              format="csv",
                                              tags={'tag1': 'test_abc', 'tag2': 'auto_xyz'},
                                              keywords=["None", "sprint-n"],
                                              sources=['ftp://example.com', 'my application'])
            self.assertTrue('Package with id 12345 not found' in context.exception)

    def test_register_dataset_with_invalid_version_number(self):
        package_id = self.create_package(
            "test_register_dataset_can_create_dataset_uploading_files"
        )
        with self.assertRaises(InvalidPayloadException) as context:
            ds = self.client.register_dataset(
                package_id=package_id,
                description="new dataset api",
                s3_prefix="auto_test/20180511/",
                files=[
                    "./data/total_production_per_field - 1.csv",
                    "./data/info.txt"
                ],
                version=3.3,
                format="csv",
                tags={'tag1':'test_abc', 'tag2':'auto_xyz'},
                keywords=["None","sprint-n"],
                sources=['ftp://example.com', 'my application']
            )
            self.assertTrue("Unable to validate payload 3.3 is not of type 'integer'" in context.exception)


class DownloadDatasetTestCase(DatasetFunctionsTestCase):

    def setUp(self):
        super(DownloadDatasetTestCase, self).setUp()
        # create a package
        self.package_id = self.create_package("DownloadDatasetTestCase")

    def test_download_dataset_for_unknown_dataset_fails(self):
        with self.assertRaises(Exception):
            self.client.download_dataset("unknown")

    def test_download_dataset_retrieves_all_files_in_dataset(self):
        dataset = self.client.register_dataset(
            self.package_id,
            "test_download_dataset_retrieves_all_files_in_dataset",
            "prefix/",
            [
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ]
        )

        with tempfile.TemporaryDirectory() as dest:
            self.client.download_dataset(dataset.id, dest)

            # validate we got the expected calls
            self.s3_download_mock.assert_has_calls([
                call("s3://local-ihsm-dl-pkg-test/prefix/MSFT.csv", dest),
                call("s3://local-ihsm-dl-pkg-test/prefix/AAPL.csv", dest),
                ],
                any_order=True
            )

    def test_download_dataset_keeps_going_if_a_file_in_the_dataset_fails(self):
        def _download(_, file, dest):
            if file.endswith("AAPL.csv"):
                raise Exception("")

        dataset = self.client.register_dataset(
            self.package_id,
            "test_download_dataset_keeps_going_if_a_file_in_the_dataset_fails",
            "prefix/",
            [
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ]
        )

        with self.assertRaises(DownloadFailed):
            with patch('dli.client.s3.Client.download_file', _download) as s3_download:
                with tempfile.TemporaryDirectory() as dest:
                    self.client.download_dataset(dataset.id, dest)

                    # validate we got the expected calls
                    s3_download.assert_has_calls([
                        call("s3://local-ihsm-dl-pkg-test/prefix/MSFT.csv", dest),
                        call("s3://local-ihsm-dl-pkg-test/prefix/AAPL.csv", dest),
                        ],
                        any_order=True
                    )


@patch("dli.client.s3.build_s3fs", build_fake_s3fs)
class RegisterDatasetTestCase(SdkIntegrationTestCase):

    def set_s3_client_mock(self):
        pass

    def test_can_upload_dataset_providing_folder_with_relative_path(self):
        package_id = self.create_package(
            "test_can_upload_dataset_providing_folder_with_relative_path"
        )

        sample_data = os.path.join(
            os.path.dirname(__file__),
            'resources/yahoo'
        )

        dataset = self.client.register_dataset(
            package_id,
            "desc",
            "prefix/",
            [sample_data]
        )

        # assert the files were uploaded and that
        # their sizes have been resolved
        self.assertIn({
                "path": "s3://local-ihsm-dl-pkg-test/prefix/AAPL.csv",
                "size": os.path.getsize(os.path.join(sample_data, "AAPL.csv"))
            },
            dataset.files
        )
        self.assertIn({
                "path": "s3://local-ihsm-dl-pkg-test/prefix/MSFT.csv",
                "size": os.path.getsize(os.path.join(sample_data, "MSFT.csv"))
            },
            dataset.files
        )
