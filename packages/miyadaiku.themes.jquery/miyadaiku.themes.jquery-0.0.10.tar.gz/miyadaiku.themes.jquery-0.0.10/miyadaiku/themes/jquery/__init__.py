from miyadaiku.core.contents import bin_loader
from miyadaiku.core import config

JQUERY_MIN = 'jquery.min.js'
JQUERY = 'jquery.js'
DEST_PATH = '/static/jquery/'

def load_package(site):
    f = site.config.getbool('/', 'jquery_compressed')
    jquery = JQUERY_MIN if f else JQUERY
    src_path = 'externals/'+jquery
    
    content = bin_loader.from_package(site, __name__, src_path, DEST_PATH+jquery)
    site.contents.add(content)
    site.config.add('/', {'jquery_path': DEST_PATH+jquery})

    site.add_template_module('jquery', 'miyadaiku.themes.jquery!macros.html')
