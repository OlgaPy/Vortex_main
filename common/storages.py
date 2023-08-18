from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin
from storages.backends.gcloud import GoogleCloudStorage


class StaticFilesGoogleStorage(ManifestFilesMixin, GoogleCloudStorage):
    """Storage class for statis files."""

    bucket_name = settings.STATIC_STORAGE_BUCKET_NAME
