from backports import tempfile
from tests.common import SdkIntegrationTestCase
from unittest import skip


class SDKSamples(SdkIntegrationTestCase):
    """
    This spec is just meant to catch issues in terms of signature changes
    all the methods are included in one way or another in the SDK documentation
    as samples.

    Avoid including assertions or similar as these tests are not replacements
    for unit or integration tests on these functions.
    """

    def test_get_datasets_in_package(self):
        client = self.client
        package_id = self.create_package("test_get_datasets_in_package")

        # doc-start
        # returns list of datasets ordered by descending creation date
        datasets = client.get_package_datasets(package_id)

        print("Retrieved {} datasets.".format(len(datasets)))
        for ds in datasets:
            print((ds.id, ds.files))

    def test_download_dataset(self):
        client = self.client
        package_id = self.create_package("test_get_datasets_in_package")
        dataset = self.client.register_dataset(
            package_id,
            "test_download_dataset_retrieves_all_files_in_dataset",
            "prefix/",
            [
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ]
        )
        dataset_id = dataset.id

        with tempfile.TemporaryDirectory() as destination:
            # doc-start
            client.download_dataset(dataset_id, destination)

            import os
            os.listdir(destination)  # shows: ['AAPL.csv', 'MSFT.csv']

    def test_create_dl_dataset(self):
        client = self.client
        package_id = self.create_package("test_create_update_delete_dl_dataset")

        # doc-start
        # given a package with data lake managed storage
        # we can register and upload files into S3
        # which then can be used by your consumers
        dataset = client.register_dataset(
            package_id,
            "My Dataset for Today",
            s3_prefix="prefix/",
            files=[
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ]
        )

    def test_create_ext_dataset(self):
        client = self.client
        package_id = self.create_package_with_no_bucket(
            "test_create_update_delete_ext_dataset"
        )

        # doc-start
        # given a package with external storage, we want to register a new dataset under it
        # in this case the bucket is not managed by the data lake, so the upload
        # needs to be done manually
        dataset = client.register_dataset_metadata(
            package_id,
            "test", [
                {"path": "s3://bucket/path/to/file/A", "size": 10000},
                {"path": "s3://bucket/path/to/file/B", "size": 15222}
            ],
            tags={
                "business-date": "yesterday",
                "asset-class": "fixed-income"
            }
        )

    def test_update_and_delete_dataset(self):
        client = self.client
        package_id = self.create_package_with_no_bucket(
            "test_create_update_delete_ext_dataset"
        )
        dataset = client.register_dataset_metadata(
            package_id,
            "test",
            ["/path/to/file/A", "/path/to/file/B"],
            tags={
                "business-date": "yesterday",
                "asset-class": "fixed-income"
            }
        )

        # doc-start
        # now that we have created a dataset, and have an id (under `dataset.id`)
        # we can make changes to the metadata
        # this function for example, would change the description
        # while leaving all other attributes as they are.
        updated = client.update_dataset_metadata(
            dataset.id,
            description="correct desc."
        )

        # we can also mark the dataset as deleted
        # if we don't want it to be available for consumption anymore.
        # this call only deletes the metadata and leaves
        # the actual data intactc.
        client.delete_dataset(updated.id)
