import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import permissions


class IsYouOrIsAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow profile owner of an object to edit it.
    Assumes the model instance has an `id` attribute.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id or request.user.is_staff


def delete_file_from_s3(file_name: str) -> bool:
    """
    Delete media file from AWS S3 Bucket by its name
    """

    bucket = settings.AWS_STORAGE_BUCKET_NAME
    object_key = "media/" + file_name

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_key)
    except ClientError as e:
        logging.error(e)
        return False
    return True
