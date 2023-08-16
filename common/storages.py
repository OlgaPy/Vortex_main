from storages.backends.gcloud import GoogleCloudStorage


class MediaStorage(GoogleCloudStorage):
    """Storage class for user uploads."""
