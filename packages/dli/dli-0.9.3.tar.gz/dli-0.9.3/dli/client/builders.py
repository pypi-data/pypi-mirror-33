
class PackageBuilder:
    """
        Allows specifying the metadata a new package requires.

        Packages are parent structures that contain metadata relating
        to a collection of Datasets.

        This builder object sets sensible defaults and exposes
        helper methods on how to configure its storage options.

        See description for each parameter, and whether they are optional or mandatory.

        :param str name: Mandatory. A descriptive name of a package. It should be unique across the Data Catalogue.
        :param str description: Mandatory. A short description of a package.
        :param str data_source: Mandatory. Accepted values are: `Internal` or `External`.
                            Package is `External` if the underlying data is
                            created externally, e.g. S&P, Russell, etc.
                            Packages with data created at IHS Markit are `Internal`.
        :param str data_access: Mandatory. Accepted values are: `Restricted` or `Unrestricted`.
                            Defaults to `Restricted`.
                            If access to the package is flagged as `Restricted`,
                            package manager will have to grant or deny access to the underlying data.
                            If access is flagged as `Unrestricted`, user will be able to gain
                            access instantaneously after submitting the access request form.
        :param str visibility: Mandatory. Accepted values are: `Internal`, `Public`, `Private`.
                            Defaults to `Internal`.
                            Reserved for future use.
        :param str product: Optional. A group of packages. Packages usually sold or accessed together
                        can be associated using a Product. Future functionality will provide
                        ability to identify all packages associated with a specific product.
        :param str industry_or_sector: Optional. Industry/sector the data in the package is about.
                                   Not applicable, if the package content is not industry specific.
        :param str region: Optional. Region the data in the package is about.
                       If the package content is not geography specific this can be left blank.
        :param str content_creator: Mandatory. Account ID for the Data Lake Account
                                representing company or IHS Markit business
                                unit that has created the data.
                                Defaults to your Data Lake Account if none provided.
        :param str publisher: Mandatory. Account ID for the Data Lake Account representing
                          IHS Markit business unit that is responsible for uploading
                          the data to Data Lake.
                          Defaults to your Data Lake Account if none provided.
        :param list[str] keywords: Optional. A list of keywords that can be used to find this
                         package through the search interface.
        :param str manager: Mandatory. Account ID for the Data Lake Account representing IHS Markit
                        business unit that is responsible for creating and
                        managing access to the packages on Data Catalogue.
                        Defaults to your Data Lake Account if none provided.
        :param str confidentiality_level: Optional. Accepted values are: `Confidential`, `Public`.
                                      Data classification to confidential or public.
        :param str contract_bound: Optional. A flag to identify the packages with data
                               which is or should be bound by a contract/license.
        :param str internal_usage_rights: Optional. Accepted values are: `Yes`, `No`, `With restrictions`, `N/A`.
                                      A flag whether data can be used internally.
        :param str internal_usage_notes: Optional. Provides details, comments on internal data usage.
                                     Extension to Internal Usage Rights.
        :param str distribution_rights: Optional. Accepted values are `Yes`, `No`, `With restrictions`, `N/A`.
                                    A flag whether data can be distributed.
        :param str distribution_notes: Optional. Provides details, comments on data distribution rights.
                                   Extension to the Distribution Rights field.
        :param str derived_data_rights: Optional. Accepted values are `Yes`, `No`, `With restrictions`, `N/A`.
                                    A flag whether we have rights to derived data.
        :param str derived_data_notes: Optional. Provides details, comments on derived data.
                                   Extension to the Derived Data Rights field.
        :param str data_type: Optional. A field to indicate whether package contains time series,
                          structured, semi-structured etc. data.
        :param str frequency: Optional. A field to indicate how frequently the underlying data
                          is uploaded to Data Lake.
        :param str data_format: Optional. The file format that data is received in
                            i.e. text, csv, parquet, etc.
        :param str documentation: Optional. Documentation about this package
                              in markdown format.
    """
    def __init__(
        self,
        name,
        description,
        data_source,
        data_access=None,
        visibility=None,
        product=None,
        industry_or_sector=None,
        region=None,
        content_creator=None,
        publisher=None,
        keywords=None,
        manager=None,
        confidentiality_level=None,
        contract_bound=None,
        internal_usage_rights=None,
        internal_usage_notes=None,
        distribution_rights=None,
        distribution_notes=None,
        derived_data_rights=None,
        derived_data_notes=None,
        data_type=None,
        frequency=None,
        data_format=None,
        documentation=None
    ):
        self.content_creator = content_creator
        self.manager = manager
        self.publisher = publisher

        self.fields = {
            "name": name,
            "description": description,
            "dataSource": data_source,
            "dataAccess": data_access or "Restricted",
            "visibility": visibility or "Internal",
            "product": product,
            "industrySector": industry_or_sector,
            "region": region,
            "keywords": keywords or [],
            "confidentialityLevel": confidentiality_level,
            "contractBound": contract_bound,
            "internalUsageRights": internal_usage_rights,
            "internalUsageNotes": internal_usage_notes,
            "distributionRights": distribution_rights,
            "distributionNotes": distribution_notes,
            "derivedDataRights": derived_data_rights,
            "derivedDataNotes": derived_data_notes,
            "dataType": data_type,
            "frequency": frequency,
            "dataFormat": data_format,
            "documentation": documentation or ""
        }
        self.storage = None

    def with_data_lake_storage(self, bucket_name):
        """
        Indicate that this package's datasets will be stored
        in a data-lake owned S3 bucket.

        :param bucket_name: A unique representative name for this bucket.
                            Data Lake buckets share a common prefix which will be
                            appended to this name if the creation is successful.
        :type bucket_name: str

        :rtype: dli.client.builders.PackageBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import PackageBuilder
                
                builder = PackageBuilder(
                                name="my test package",
                                description="My package description",
                                data_source="External"
                        )
                builder = builder.with_data_lake_storage("data-lake-bucket-name")
                package = dl.register_package(builder)
        """
        self.storage = {
            "dataStorage": "S3",
            "createS3Bucket": True,
            "s3Bucket": bucket_name
        }
        return self

    def with_external_s3_storage(
        self,
        bucket_name
    ):
        """
        Indicate that this package's datasets will be stored
        in a self-managed S3 bucket outside of the Data Lake.

        :param bucket_name: Name of the bucket you want to link to this package
        :type bucket_name: str

        :rtype: dli.client.builders.PackageBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import PackageBuilder

                builder = PackageBuilder(
                                name="my test package",
                                description="My package description",
                                data_source="External"
                        )
                builder = builder.with_external_s3_storage(
                    bucket_name="external-s3-bucket-name"
                )
                package = dl.register_package(builder)
        """
        self.storage = {
            "dataStorage": "S3",
            "createS3Bucket": False,
            "s3Bucket": bucket_name
        }
        return self

    def with_external_storage(self, location):
        """
        Allows specifying a non S3 location where
        the package's datasets reside.

        The location will be kept for informational purposes only.

        :param location: a connection string or identifier
                         where this package resides.
        :type location: str

        :rtype: dli.client.builders.PackageBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import PackageBuilder

                builder = PackageBuilder(
                                name="my test package",
                                description="My package description",
                                data_source="External"
                        )
                builder = builder.with_external_storage("external-storage-location")
                package = dl.register_package(builder)
        """
        self.storage = {
            "dataStorage": "Other",
            "dataLocation": location
        }
        return self

    def build(self):
        # if no storage provided, then by default we set it to `Other`
        if not self.storage:
            raise Exception(
                "No storage option was specified. Please use one of the following methods: "
                "`with_data_lake_storage`, `with_external_s3_storage`, `with_external_storage`"
            )

        payload = dict(self.fields)
        payload.update({
            "contentCreator": {"accountId": self.content_creator},
            "publisher": {"accountId": self.publisher},
            "manager": {"accountId": self.manager},
        })
        payload.update(self.storage)

        # clean not set entries
        payload = {k: v for k, v in payload.items() if v is not None}
        return payload
