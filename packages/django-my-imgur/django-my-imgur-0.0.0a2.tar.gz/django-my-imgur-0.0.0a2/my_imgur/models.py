import logging
import os
import tempfile

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.query import QuerySet

import pyimgur

from .settings import (ACCESS_REFRESH_TOKEN, ACCESS_TOKEN, CLIENT_ID,
                       CLIENT_SECRET)

logger = logging.getLogger(__name__)


class MyQuerySet(QuerySet):
    def delete(self):
        # Use individual queries to the attachment is removed.
        for item in self.all():
            item.delete()


class Album(models.Model):
    PUBLIC = 'public'
    HIDDEN = 'hidden'
    SECRET = 'secret'

    default = models.BooleanField(default=False)
    album_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    link = models.URLField()
    PRIVACY_CHOICES = (
        (PUBLIC, 'public'),
        (HIDDEN, 'hidden'),
        (SECRET, 'secret'),
    )
    privacy = models.CharField(max_length=6, choices=PRIVACY_CHOICES, default=HIDDEN)

    objects = MyQuerySet.as_manager()

    def clean(self):
        if self.album_id:
            try:
                # Login into imgur
                im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
                # Get that album from imgur
                album = im.get_album(self.album_id)
            except Exception as error:
                if 'Not Found for url' in str(error):
                    raise ValidationError('This album ID %s is not exists, can\'t update' % self.album_id)
                else:
                    logger.error(error)
                    raise ValidationError('%s' % str(error))

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.default:
            Album.objects.filter(default=True).update(default=False)
        else:
            default_true = Album.objects.filter(default=True)
            if len(default_true) == 0:
                self.default = True

        im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
        if self.album_id:
            album = im.get_album(self.album_id)
            album.update(self.title, self.description, privacy=self.privacy)
        else:
            album = im.create_album(self.title, self.description, privacy=self.privacy)
        self.album_id = album.id
        self.link = album.link
        super(Album, self).save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.album_id:
            try:
                im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
                album = im.get_album(self.album_id)
                album.delete()
            except Exception as error:
                if 'Not Found for url' in str(error):
                    pass
                else:
                    logger.error(error)
                    raise
        super(Album, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Image(models.Model):
    default = models.BooleanField(default=False)
    image_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    use_direct_image_link = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True,)

    objects = MyQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self._prev_album = self.album

    def clean(self):
        # Login into imgur
        im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
        if self.image_id and not self.image:
            try:
                # Get that image from imgur
                imageTmp = im.get_image(self.image_id)
            except Exception as error:
                if 'Not Found for url' in str(error):
                    raise ValidationError('This image ID %s is not exists, can\'t update.' % self.image_id)
                else:
                    logger.error(error)
                    raise ValidationError('%s' % str(error))
        if self.album:
            try:
                # Get that album from imgur
                album = im.get_album(self.album.album_id)
            except Exception as error:
                if 'Not Found for url' in str(error):
                    raise ValidationError('This album ID %s is not exists.' % self.album.album_id)
                else:
                    logger.error(error)
                    raise ValidationError('%s' % str(error))

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Confirm this is default image
        if self.default:
            # Set default of other image to False
            Image.objects.filter(default=True).update(default=False)
        else:
            # Get all image which has default is True
            default_true = Image.objects.filter(default=True)
            # Confirm there are no default image
            if len(default_true) == 0:
                # Set this is default image
                self.default = True

        # Confirm user doesn't want to upload to imgur
        # just use direct link
        if self.use_direct_image_link:
            # Confirm we already have a imgur image ID
            if self.image_id:
                # Login into imgur
                im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
                # Get that image from imgur
                imageTmp = im.get_image(self.image_id)
                # Delete it
                imageTmp.delete()
                self.image_id = None
                self.album = None
        else:
            # Login into imgur
            im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
            # Confirm user has upload a new image
            if self.image:
                # Create temp image file
                tempf, tempfn = tempfile.mkstemp()
                # Create temp image variable
                imageTmp = None
                # Write the new image to temp file
                try:
                    for chunk in self.image.chunks():
                        os.write(tempf, chunk)
                except:
                    logger.error('Problem with the input file %s' % self.image.name)
                    raise

                # Confirm we already have a imgur image ID
                if self.image_id:
                    try:
                        # Get that image from imgur
                        imageTmp = im.get_image(self.image_id)
                        # Delete it
                        imageTmp.delete()
                    except:
                        pass
                # Confirm the temp image file is exists
                if os.path.isfile(tempfn):
                    # Create temp album variable
                    albumTmp = None
                    # Confirm user already set an album for this image
                    if self.album:
                        # Set imgur album ID to temp album variable
                        albumTmp = self.album.album_id

                    # Upload the new image
                    try:
                        imageTmp = im.upload_image(tempfn, title=self.title,
                                                   description=self.description, album=albumTmp)
                    except Exception as error:
                        logger.error(error)
                        raise
                    finally:
                        os.remove(tempfn)
                # Confirm temp image is valid
                if imageTmp:
                    # Update model information
                    self.image_id = imageTmp.id
                    self.link = imageTmp.link
            # Confirm no new image, already has imgur ID
            # maybe we update image title or description
            elif self.image_id:
                try:
                    imageTmp = im.get_image(self.image_id)
                    is_updated = imageTmp.update(self.title, description=self.description)
                    # Confirm no new update, reset information
                    if is_updated == False:
                        self.title = imageTmp.title
                        self.description = imageTmp.description
                    # Confirm album has been changed
                    if self._prev_album != self.album:
                        # Confirm the previous album is valid
                        if self._prev_album:
                            try:
                                # Remove the image from the previous album
                                albumTmp = im.get_album(self._prev_album.album_id)
                                albumTmp.remove_images(self.image_id)
                            except:
                                logger.error(error)
                        # Confirm the new album is valid
                        if self.album:
                            # Add the image to the new album
                            albumTmp = im.get_album(self.album.album_id)
                            albumTmp.add_images(self.image_id)
                except Exception as error:
                    logger.error(error)
                    raise
        # Always set the image to None
        self.image = None

        super(Image, self).save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.image_id:
            try:
                im = pyimgur.Imgur(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCESS_REFRESH_TOKEN)
                image = im.get_image(self.image_id)
                image.delete()
            except Exception as error:
                if 'Not Found for url' in str(error):
                    pass
                else:
                    logger.error(error)
                    raise
        super(Image, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
