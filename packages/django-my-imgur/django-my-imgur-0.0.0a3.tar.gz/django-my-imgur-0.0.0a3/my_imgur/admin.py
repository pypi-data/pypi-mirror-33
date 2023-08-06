from django.contrib import admin

from .models import Album, Image


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'album_id', 'link', 'default',)
    readonly_fields = ('album_id', 'link',)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_id', 'link', 'default', 'use_direct_image_link', 'album', )
    readonly_fields = ('image_id',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if obj.use_direct_image_link is True:
                return self.readonly_fields + ('album', 'default', 'image', 'use_direct_image_link', )
            else:
                return self.readonly_fields + ('use_direct_image_link', 'link',)
        return self.readonly_fields


admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
