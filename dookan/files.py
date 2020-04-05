from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

SYS_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# settings.MEDIA_ROOT = os.path.join(SYS_BASE_DIR, "media/images/")

fs = FileSystemStorage(location="media/images/")

def image_upload_path(instance, filename):
    return "full/{1}".format(instance.id,filename)

def md_image_upload_path(instance, filename):
    return "medium/{1}".format(instance.id,filename)

def sm_image_upload_path(instance, filename):
    return "small/{1}".format(instance.id,filename)


def rename_image(id, title, image):
    image_data = image.name.split("/")

    if title is None:
        if id is None:
            image_name = image_data[0].split(".")[0]
            if len(image_name) > 15:
                image_name = image_name[0:15]
        else:
            image_name = image_data[1].split(".")[0]
            if len(image_name) > 15:
                image_name = image_name[0:15]
        title = image_name
    else:
        initial_path = image.path
        if id is None:
            image.name = title+image_data[0].split(".")[1]
        else:
            image.name = image_data[0]+'/'+title+image_data[1].split(".")[1]

        new_path = settings.MEDIA_ROOT + image.name