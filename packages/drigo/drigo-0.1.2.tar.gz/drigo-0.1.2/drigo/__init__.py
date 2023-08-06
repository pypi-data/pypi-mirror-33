from .drigo import *

__version__ = "0.1.2"

# Check the GDAL_DATA environment variable
if "GDAL_DATA" not in os.environ:
    raise Exception('The GDAL_DATA environment variable is not set\n')
elif not os.path.isdir(os.getenv("GDAL_DATA")):
    raise Exception(
        'The GDAL_DATA environment folder does not exist:\n'
        '  {}'.format(os.getenv("GDAL_DATA")))
