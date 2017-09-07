from os.path import join, dirname, abspath
from os import environ
from syncloud_files.web import create_web_app

def detect_data_dir():
    if 'SNAP_COMMON' in environ:
        return environ['SNAP_COMMON']
    return '/opt/data/files'

app = create_web_app(detect_data_dir())

if __name__ == '__main__':
    app.run(debug=True, port=5001)