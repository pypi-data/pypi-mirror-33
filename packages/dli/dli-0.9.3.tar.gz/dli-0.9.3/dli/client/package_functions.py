import logging
from dli.siren import siren_to_entity, siren_to_dict
from dli.client.exceptions import PackageNotFoundException, NoAccountSpecified


logger = logging.getLogger(__name__)


class PackageFunctions(object):
    """
    A mixin providing common package operations
    """
    def get_s3_access_keys_for_package(self, package_id, refresh=False):
        """
        Retrieve S3 access keys for the specified account to access the
        specified package. The retrieved keys and session token will be stored
        in the client context.

        :param package_id: The id of the package
        :type package_id: str
        :param refresh: Optional flag to force refresh the token.
        :type refresh: bool

        :returns: A dictionary containing the AWS keys, package id and session
                token. For example:


                .. code-block:: python

                    {
                       "accessKeyId": "39D19A440AFE452B9",
                       "packageId": "d0b545dd-83ee-4293-8dc7-5d0607bd6b10",
                       "secretAccessKey": "F426A93CDECE45C9BFF8F4F19DA5CB81",
                       "sessionToken": "C0CC405803F244CA99999"
                    }
        """
        if package_id in self.ctx.s3_keys and not refresh:
            return self.ctx.s3_keys[package_id]

        # otherwise we go and attempt to fetch one from the API
        root = self.ctx.get_root_siren()
        pf = root.package_forms()
        keys = pf.request_access_keys(package_id=package_id)

        val = {
            "accessKeyId": keys.accessKeyId,
            "packageId": keys.packageId,
            "secretAccessKey": keys.secretAccessKey,
            "sessionToken": keys.sessionToken
        }

        # cache the key for future usages
        self.ctx.s3_keys[package_id] = val

        return val

    def get_package(self, package_id):
        """
        Fetches package metadata for an existing package. This calls returns a python namedtuple containing information of the package.

        :param package_id: The id of the package
        :type package_id: str

        :returns: A package instance
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                package_id = "your-package-id"
                package = dl.get_package(package_id)

        """
        p = self._get_package(package_id)
        if not p:
            logger.warn("No package found with id `%s`", package_id)
            return

        return siren_to_entity(p)

    def get_package_datasets(self,
        package_id,
        description=None,
        format=None,
        version=None,
        keywords=None,
        tags=None,
        count=100
    ):
        """
        Returns a list of all datasets registered under a package
        and allows providing extra criteria to find specific
        entries

        :param str package_id: The id of the package
        :param str description: A string to partially match in the dataset description
        :param str format: The format of the dataset: csv, parquet, etc.
        :param int version: Format an specific version of dataset
        :param list[str] keywords: A list of keywords that need to be present in a dataset.
        :param dict[str,str] tags: A dictionary of tags that need to be present in a dataset.
        :param int count: Optional count of datasets to be returned.

        :returns: list of all datasets registered under the package
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                datasets = self.client.get_package_datasets(
                    package_id,
                    version=1,
                    keywords=["key1"],
                    tags={"tag1": "value1"}
                )
        """
        package = self._get_package(package_id)
        if package is None:
            raise Exception("No package could be found with id %s" % package_id)

        if keywords:
            keywords = ",".join(keywords)
        if tags:
            tags = ",".join(["%s:%s" % (str(k), str(v))for k,v in tags.items()])

        datasets = package.search_datasets(
            description=description,
            version=version,
            format=format,
            keywords=keywords,
            tags=tags,
            page_size=count
        ).get_entities(rel="dataset")
        return [siren_to_entity(d) for d in datasets]

    def register_package(
        self,
        package_builder
    ):
        """
        Submit a request to create a new package in the data catalog.

        :param package_builder: An instance of PackageBuilder
        :type package_builder: dli.client.builders.PackageBuilder

        :returns: a newly created Package
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                from dli.client.builders import PackageBuilder
                
                builder = PackageBuilder(
                                name="my test package",
                                description="My package description",
                                data_source="External"
                          )
                builder = builder.with_data_lake_storage("my-bucket-name")
                package = dl.register_package(builder)
        """
        # get my accounts so that we can use them as a default for all the roles
        if not package_builder.content_creator or not package_builder.publisher or not package_builder.manager:
            accounts = self.get_my_accounts()
            if len(accounts) > 1:
                raise NoAccountSpecified(accounts)

            default_account = accounts[0].id
            if not package_builder.content_creator:
                logger.info("Assigning ourselves as content_creator as no value was provided.")
                package_builder.content_creator = default_account
            if not package_builder.manager:
                logger.info("Assigning ourselves as manager as no value was provided.")
                package_builder.manager = default_account
            if not package_builder.publisher:
                logger.info("Assigning ourselves as publisher as no value was provided.")
                package_builder.publisher = default_account

        package = package_builder.build()
        pf = self.get_root_siren().package_forms()
        return siren_to_entity(pf.register_package(__json=package))

    def edit_package(
        self,
        package_id,
        name=None,
        description=None,
        data_source=None,
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
        """
        Updates one or more fields in a package.
        If a field is passed as ``None`` then the field will not be updated.

        :param name: Mandatory. A descriptive name of a package. It should be unique across the Data Catalogue.
        :type name: str
        :param description: Mandatory. A short description of a package.
        :type description: str
        :param data_source: Mandatory. Accepted values are: `Internal` or `External`.
                            Package is `External` if the underlying data is
                            created externally, e.g. S&P, Russell, etc.
                            Packages with data created at IHS Markit are `Internal`.
        :type data_source: str
        :param data_access: Mandatory. Accepted values are: `Restricted`, `Unrestricted`.
                            If access to the package is flagged as `Restricted`,
                            package manager will have to grant or deny access to the underlying data.
                            If access is flagged as `Unrestricted`, user will be able to gain
                            access instantaneously after submitting the access request form.
        :type data_access: str
        :param visibility:  Mandatory. Accepted values are: `Internal`, `Public`, `Private`.
                            Reserved for future use.
        :type visibility: str
        :param product: Optional. A group of packages. Packages usually sold or accessed together
                        can be associated using a Product. Future functionality will provide
                        ability to identify all packages associated with a specific product.
        :type product: str
        :param industry_or_sector: Optional. Industry/sector the data in the package is about.
                       Not applicable, if the package content is not industry specific.
        :type industry_or_sector: str                                   
        :param region: Optional. Region the data in the package is about.
                       If the package content is not geography specific this can be left blank.
        :type region: str
        :param content_creator: Mandatory. Account ID for the Data Lake Account
                                representing company or IHS Markit business
                                unit that has created the data.
        :type content_creator: str
        :param publisher: Mandatory. Account ID for the Data Lake Account representing
                          IHS Markit business unit that is responsible for uploading
                          the data to Data Lake.
        :type publisher: str
        :param keywords: Optional. A list of keywords that can be used to find this
                         package through the search interface.
        :type keywords: list[str]
        :param manager: Mandatory. Account ID for the Data Lake Account representing IHS Markit
                        business unit that is responsible for creating and
                        managing access to the packages on Data Catalogue.
        :type manager: str
        :param confidentiality_level: Optional. Accepted values are: `Confidential`, `Public`.
                                      Data classification to confidential or public.
        :type confidentiality_level: str
        :param contract_bound: Optional. A flag to identify the packages with data
                               which is or should be bound by a contract/license.
        :type contract_bound: str
        :param internal_usage_rights: Optional. Accepted values are: `Yes`, `No`, `With restrictions`, `N/A`.
                                      A flag whether data can be used internally.
        :type internal_usage_rights: str
        :param internal_usage_notes: Optional. Provides details, comments on internal data usage.
                                     Extension to Internal Usage Rights.
        :type internal_usage_notes: str
        :param distribution_rights: Optional. Accepted values are `Yes`, `No`, `With restrictions`, `N/A`.
                                    A flag whether data can be distributed.
        :type distribution_rights: str
        :param distribution_notes: Optional. Provides details, comments on data distribution rights.
                                   Extension to the Distribution Rights field.
        :type distribution_notes: str
        :param derived_data_rights: Optional. Accepted values are `Yes`, `No`, `With restrictions`, `N/A`.
                                    A flag whether we have rights to derived data.
        :type derived_data_rights: str
        :param derived_data_notes: Optional. Provides details, comments on derived data.
                                   Extension to the Derived Data Rights field.
        :type derived_data_notes: str
        :param data_type: Optional. A field to indicate whether package contains time series,
                          structured, semi-structured etc. data.
        :type data_type: str
        :param frequency: Optional. A field to indicate how frequently the underlying data
                          is uploaded to Data Lake.
        :type frequency: str
        :param data_format: Optional. The file format that data is received in
                            i.e. text, csv, parquet, etc.
        :type data_format: str
        :param documentation: Optional. Documentation about this package
                              in markdown format.
        :type documentation: str

        :returns: Updated package.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                dl.edit_package(
                    package_id,
                    data_access="Restricted",
                    visibility="Internal"
                )
        """

        package = self._get_package(package_id)
        if not package:
            raise PackageNotFoundException(package_id)

        def _account_for(id):
            return {"accountId": id} if id else None

        fields = {
            "name": name,
            "description": description,
            "dataSource": data_source,
            "dataAccess": data_access,
            "visibility": visibility,
            "product": product,
            "industrySector": industry_or_sector,
            "region": region,
            "keywords": keywords,
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
            "documentation": documentation,

            # accounts are slightly different as we post a complex json back
            "publisher": _account_for(publisher or package.publisher["accountId"]),
            "manager": _account_for(manager or package.manager["accountId"]),
            "contentCreator": _account_for(content_creator or package.contentCreator["accountId"])
        }

        # we can't just post back the siren object for some reason
        # as it can't be deserialised
        # also tags are converted in the backend (they shouldn't in the DB)
        # so we need to reformat them
        package_as_dict = siren_to_dict(package)

        # clean the package dict with fields that aren't known to us
        for key in list(package_as_dict.keys()):
            if key not in fields:
                del package_as_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        package_as_dict.update(payload)

        pf = self.get_root_siren().package_forms()
        result = pf.edit_package(package_id=package_id, __json=package_as_dict)
        return siren_to_entity(result)

    def search_packages(self, term):
        """
        Search packages given a particular set of keywords

        :param term: The search term
        :type term: str

        :returns: A list of package entities
        """
        packages = self.get_root_siren().list_packages(query=term)
        return packages

    def delete_package(self, package_id):
        """
        Performs deletion of an existing package. This will delete all underlying datasets for the package as well.

        :param package_id: The id of the package to be deleted
        :type package_id: str

        :returns:

        - **Sample**

        .. code-block:: python

                dl.delete_package(package_id)

        """
        package = self._get_package(package_id)
        if package:
            package.delete_package(package_id=package_id)
        else:
            raise PackageNotFoundException(package_id)

    def get_my_accounts(self):
        """
        Returns a list of all the accounts associated to my session.
        """
        result = self.get_root_siren().list_my_accounts()
        accounts = result.get_entities(rel="")
        return [siren_to_entity(a) for a in accounts]

    def get_my_consumed_packages(self, count=100):
        """
        Returns a list of all the packages my account has access to.

        :param int count: The number of items to retrieve, defaults to 100.
        """
        result = self.get_root_siren().list_consumed_packages(page_size=count)
        packages = result.get_entities(rel="package")
        return [siren_to_entity(p) for p in packages]

    #
    # Private functions
    #

    def _get_package(self, package_id):
        return self.get_root_siren().get_package(package_id=package_id)
