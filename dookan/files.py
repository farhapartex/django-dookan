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


def rename_image(new_name, instance):
    try:
        # get image size from settings.py file
        md_size = settings.MID_IMAGE_SIZE
        sm_size = settings.SM_IMAGE_SIZE
    except :
        # if no size get from settings.py, default size will be this
        md_size = (768,1024)
        sm_size = (265, 300)

    images = [instance.image, instance.md_image, instance.sm_image]

    for i in range(0, len(images)):
        image_data = images[i].name.split("/")
        initial_path = images[i].path
        if i == 0:
            images[i].name = image_data[0]+'/'+ new_name +"."+ image_data[1].split(".")[-1]
        elif i == 1:
            images[i].name = image_data[0]+'/'+ new_name +str(md_size[0])+"x"+str(md_size[1]) +"."+ image_data[1].split(".")[-1]
        elif i == 2:
            images[i].name = image_data[0]+'/'+ new_name +str(sm_size[0])+"x"+str(sm_size[1]) +"."+ image_data[1].split(".")[-1]
        
        new_path = settings.MEDIA_ROOT + images[i].name
        os.rename(initial_path, new_path)

    return tuple(images)