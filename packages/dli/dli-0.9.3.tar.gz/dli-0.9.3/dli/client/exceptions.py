class DatalakeException(Exception):
    pass


class DatasetNotFoundException(DatalakeException):
    pass


class PackageNotFoundException(DatalakeException):

    def __init__(self, package_id=None, message=None):
        if not package_id and not message:
            message = "Package not found"

        self.message = (
            message or 'Package with id {} not found'.format(package_id)
        )

        super(PackageNotFoundException, self).__init__(self.message)


class InvalidPayloadException(DatalakeException):
    pass


class S3FileDoesNotExist(DatalakeException):
    pass


class DownloadDestinationNotValid(DatalakeException):
    """
    Raised when a download destination is not a directory
    """
    pass


class DownloadFailed(DatalakeException):
    pass


class NoAccountSpecified(DatalakeException):

    def __init__(self, accounts):
        self.accounts = accounts
        self.message = (
            "Unable to default the account for content_creator, publisher and/or manager "
            "due to multiple accounts being attached to this API key. "
            "Your accounts are: %s" % [(a.id, a.name) for a in accounts]
        )
        super(NoAccountSpecified, self).__init__(self.message)


class UnAuthorisedAccessException(DatalakeException):
    pass


class InsufficientPrivilegeException(DatalakeException):
    pass
