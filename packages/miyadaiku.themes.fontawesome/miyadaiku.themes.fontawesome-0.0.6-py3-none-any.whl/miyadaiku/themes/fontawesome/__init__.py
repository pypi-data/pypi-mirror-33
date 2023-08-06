from miyadaiku.core.contents import bin_loader
from miyadaiku.core import config

FONTAWESOME_MIN = 'font-awesome.min.css'
FONTAWESOME = 'font-awesome.css'
DEST_PATH = '/static/fontawesome/css/'

def load_package(site):
    f = site.config.get('/', 'fontawesome_compressed')
    f = config.to_bool(f)
    fontawesome = FONTAWESOME_MIN if f else FONTAWESOME
    src_path = 'externals/css/'+fontawesome
    
    content = bin_loader.from_package(site, __name__, src_path, DEST_PATH+fontawesome)
    site.contents.add(content)
    site.config.add('/', {'fontawesome_path': DEST_PATH+fontawesome})

    site.add_template_module('fontawesome', 'miyadaiku.themes.fontawesome!macros.html')
