import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response

from applications.notification.models import Notification
from applications.user_profile.models import User
from applications.user_profile.serializers import UserListSerializer


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


def user_contacts_add_delete(self, request, **kwargs):
    user = self.request.user

    add_or_delete = {
        "add": user.contacts.add,
        "delete": user.contacts.remove
    }.get(kwargs.get("command"))

    contacts_to_add_list = request.data["contacts"]

    added_list = list()
    failed_list = list()

    for contact_pk in contacts_to_add_list:
        try:
            contact = User.objects.get(pk=contact_pk)
            add_or_delete(contact)
            added_list.append(contact_pk)

            if kwargs.get("command") == "add":
                Notification.objects.create(
                    name="You have a new contact",
                    user_id=contact_pk,
                    json_data=UserListSerializer(user).data,
                    content=f"{user.username} added to the list of your contact."
                )
        except User.DoesNotExist:
            failed_list.append(contact_pk)

    return Response({
        "successful_list": added_list,
        "failed_list": failed_list,
    })
