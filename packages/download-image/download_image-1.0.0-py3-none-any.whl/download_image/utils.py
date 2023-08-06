import uuid
import requests
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

ACCEPTED_FILE_FORMATS = ("gif", "png", "jpeg")

def download_image_as(url, file_format, file_name=None):
    # TODO: Attempt to get format from end of url string.
    # Ensure the file format is lowercase.
    file_format = file_format.lower()
    # Ensure the file format doesnt starts with a period.
    if file_format.startswith("."):
        file_format = "".join(file_format.split(".")[1:])
    # Ensure the file format is one that we accept.
    if file_format not in ACCEPTED_FILE_FORMATS:
        raise Exception("Not an accepted format. ({})".format(file_format))
    # Ensure the url doesnt start with no protocol.
    if url.startswith('//'):
        url = url.split('//')[1]
    # Get the response data.
    response = requests.get('http://' + url)
    # If we failed to get a response, raise an exception.
    if response.status_code != 200:
        raise Exception("Failed to download image at url {}".format(url))
    # Create a new copy of the image we downloaded in memory.
    infile = Image.open(BytesIO(response.content))
    if infile.mode != 'RGB':
        infile = infile.convert('RGB')
    outfile = BytesIO()
    # Save the memory file as a formatted image.
    infile.save(outfile, format=file_format.upper())
    # Create a universal fileanme if we don't get one to use.
    if file_name is None:
        file_name = "{prefix}.{suffix}".format(
            prefix=uuid.uuid4().hex,
            suffix=file_format
        )
    else:
        # Ensure the file name prefix is formatted appropriately.
        # Ensure the file name suffix is correct.
        bits = file_name.split(".")
        prefix_bits = bits[:-1]
        suffix = bits[-1]
        if suffix is not file_format:
            suffix = file_format
        file_name = "{}.{}".format("_".join(prefix_bits), suffix)
    # Create the content type string.
    content_type = "image/{}".format(file_format)
    # Get the byte size.
    content_length = outfile.getbuffer().nbytes
    return InMemoryUploadedFile(outfile,
                                None,
                                file_name,
                                content_type,
                                content_length,
                                None)

def download_image_as_gif(url, file_name=None):
    return download_image_as(url, "GIF", file_name)

def download_image_as_jpeg(url, file_name=None):
    return download_image_as(url, "JPEG", file_name)

def download_image_as_png(url, file_name=None):
    return download_image_as(url, "PNG", file_name)

