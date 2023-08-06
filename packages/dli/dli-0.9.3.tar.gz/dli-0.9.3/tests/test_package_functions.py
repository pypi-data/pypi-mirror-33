import logging
import datetime

from unittest import skip
from tests.common import SdkIntegrationTestCase
from dli.client.exceptions import PackageNotFoundException, NoAccountSpecified
from dli.client.builders import PackageBuilder


logger = logging.getLogger(__name__)


class PackageFunctionsTestCase(SdkIntegrationTestCase):

    def test_get_unknown_package_returns_none(self):
        self.assertIsNone(self.client.get_package("unknown"))

    def test_get_package_returns_non_siren_response(self):
        package_id = self.create_package(
            name="test_get_package_returns_non_siren_response"
        )
        package = self.client.get_package(package_id)
        self.assertEqual(package.id, package_id)

    def test_can_delete_package(self):
        package_id = self.create_package_with_no_bucket(
            "test_can_delete_package"
        )
        dataset = self.client.register_dataset_metadata(
            package_id,
            "test",
            ["/path/to/file/A", "/path/to/file/B"]
        )

        self.client.delete_package(package_id)

        self.assertIsNone(self.client.get_package(package_id))
        self.assertIsNone(self.client.get_dataset(dataset.id))

    def test_delete_unknown_package_raises_exception(self):
        with self.assertRaises(PackageNotFoundException):
            self.client.delete_package("unknown")

    def test_get_my_consumed_packages(self):
        package_1 = self.create_package(
            name="test_get_my_consumed_packages"
        )
        package_2 = self.create_package(
            name="test_get_my_consumed_packages"
        )

        packages = self.client.get_my_consumed_packages(count=1000)
        package_ids = [package.id for package in packages]

        self.assertIn(package_1, package_ids)
        self.assertIn(package_2, package_ids)


class FilterDatasetTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(FilterDatasetTestCase, self).setUp()
        self.files = ["/path/to/file/A", "/path/to/file/B"]

    def test_get_package_datasets_raises_exception_if_package_does_not_exists(self):
        with self.assertRaises(Exception):
            self.client.get_package_datasets("unknown")

    def test_get_package_datasets_returns_empty_when_no_datasets(self):
        package_id = self.create_package(
            name="test_get_package_datasets_returns_empty_when_no_datasets"
        )
        datasets = self.client.get_package_datasets(package_id)
        self.assertEqual(datasets, [])

    def test_get_package_datasets_returns_datasets_for_package(self):
        package_id = self.create_package_with_no_bucket(
            name="test_get_package_datasets_returns_datasets_for_package"
        )

        self.client.register_dataset_metadata(
            package_id=package_id,
            files=self.files,
            description="dataset 1",
            version=1,
            keywords=["key1", "key2"],
            tags={
                "tag1": "value1",
                "tag2": "value2"
            }
        )
        self.client.register_dataset_metadata(
            package_id=package_id,
            files=self.files,
            description="dataset 2",
            version=1,
            keywords=["key3", "key4"],
            tags={
                "tag1": "value1",
                "tag3": "value3"
            }
        )

        datasets = self.client.get_package_datasets(
            package_id,
            version=1,
            keywords=["key1"],
            tags={"tag1": "value1"}
        )
        self.assertEqual(len(datasets), 1)


class RegisterPackageTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(RegisterPackageTestCase, self).setUp()

        self.builder = PackageBuilder(
            name="RegisterPackageTestCase" + str(datetime.datetime.now()),
            description="My package description",
            data_source="External",
            content_creator="datalake-mgmt",
            publisher="datalake-mgmt",
            manager="datalake-mgmt"
        )

    def test_can_not_create_package_without_location(self):
        with self.assertRaises(Exception):
            self.client.register_package(self.builder)

    def test_can_create_package_with_other_location(self):
        builder = self.builder.with_external_storage(
            location="jdbc://connectionstring:1232/my-db"
        )
        package = self.client.register_package(builder)

        self.assertIsNotNone(package)
        self.assertEqual(package.description, "My package description")
        self.assertEqual(package.dataStorage, "Other")

    def test_can_create_package_with_external_bucket(self):
        builder = self.builder.with_external_s3_storage(
            bucket_name="my-happy-external-bucket"
        )

        package = self.client.register_package(builder)
        self.assertIsNotNone(package)
        self.assertEqual(package.dataStorage, "S3")
        self.assertEqual(package.s3Bucket, "my-happy-external-bucket")

    def test_can_create_package_with_data_lake_bucket(self):
        builder = self.builder.with_data_lake_storage("my-happy-bucket")
        package = self.client.register_package(builder)

        self.assertIsNotNone(package)
        self.assertEqual(package.dataStorage, "S3")
        self.assertEqual(package.s3Bucket, "local-ihsm-dl-pkg-my-happy-bucket")

    def test_can_not_default_accounts_if_api_key_has_multiple_accounts(self):
        builder = self.builder.with_data_lake_storage("my-happy-bucket")
        builder.manager = None

        with self.assertRaises(NoAccountSpecified):
            self.client.register_package(builder)

    def test_edit_unknown_package_raises_unknown_package_exception(self):
        with self.assertRaises(PackageNotFoundException):
            self.client.edit_package(package_id="unknown")

    def test_edit_package_allows_changing_single_field(self):
        builder = self.builder.with_data_lake_storage("my-happy-bucket")
        package = self.client.register_package(builder)

        edited = self.client.edit_package(
            package.id, description="enhanced description"
        )
        self.assertEqual(edited.id, package.id)
        self.assertEqual(edited.description, "enhanced description")

        # accounts were not changed
        self.assertEqual(edited.manager, package.manager)
        self.assertEqual(edited.publisher, package.publisher)
        self.assertEqual(edited.contentCreator, package.contentCreator)

        # name is still the same
        self.assertEqual(edited.name, package.name)

    def test_edit_can_change_account_ids(self):
        builder = self.builder.with_data_lake_storage("my-happy-bucket")
        package = self.client.register_package(builder)

        edited = self.client.edit_package(
            package.id,
            publisher="iboxx"
        )

        self.assertEqual(edited.id, package.id)
        self.assertEqual(edited.publisher["accountId"], "iboxx")
