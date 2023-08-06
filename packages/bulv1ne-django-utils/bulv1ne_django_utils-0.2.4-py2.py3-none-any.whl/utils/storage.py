import mimetypes
from io import StringIO

import boto3
from django.conf import settings
from django.contrib.staticfiles.storage import (
    ManifestFilesMixin, StaticFilesStorage)
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from pipeline.storage import PipelineMixin


class PipelineManifestStorage(PipelineMixin, ManifestFilesMixin, StaticFilesStorage):
    pass


class S3HeadCacheMixin:
    def get_cache_key(self, name):
        return 'storages_meta__{}'.format(name)

    def get_head(self, name, use_cache=True):
        if use_cache:
            data = cache.get(self.get_cache_key(name))
            if data:
                return data
        data = self.s3client.head_object(Bucket=self.bucket, Key=name)
        cache.set(self.get_cache_key(name), data)
        return data

    def reset_head(self, name):
        cache.delete(self.get_cache_key(name))


@deconstructible
class S3MediaStorage(Storage, S3HeadCacheMixin):
    def __init__(self):
        self.s3client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket = settings.MEDIA_BUCKET

    def delete(self, name):
        self.s3client.delete_object(Bucket=self.bucket, Key=name)

    def exists(self, name):
        try:
            self.get_head(name, use_cache=False)
            return True
        except Exception:
            return False

    def size(self, name):
        return self.get_head(name)['ContentLength']

    def url(self, name):
        return 'https://s3-{aws_region}.amazonaws.com/{bucket}/{key}'.format(
            aws_region=settings.AWS_REGION,
            bucket=self.bucket,
            key=name,
        )

    def get_modified_time(self, name):
        return self.get_head(name)['LastModified']

    def _open(self, name, mode='rb'):
        response = self.s3client.get_object(Bucket=self.bucket, Key=name)
        return ContentFile(response['Body'].read())

    def _save(self, name, content):
        if isinstance(content.file, StringIO):
            content = ContentFile(content.read().encode('utf-8'), content.name)
        self.s3client.put_object(
            Bucket=self.bucket,
            Key=name,
            Body=content,
            ACL='public-read',
            ContentType=mimetypes.guess_type(name)[0]
        )
        self.reset_head(name)
        return name
