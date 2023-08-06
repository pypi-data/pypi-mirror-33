def make_s3_token_refresher(package_functions, package_id):

    def s3_token_refresher():
        return package_functions.get_s3_access_keys_for_package(package_id, refresh=True)

    return s3_token_refresher
