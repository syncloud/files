# block to import lib folder
import sys
from os import listdir
from os.path import join, dirname, isdir, abspath

app_path = abspath(join(dirname(__file__), '..'))

lib_path = join(app_path, 'lib')
libs = [join(lib_path, item) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.append(x), libs)
# end of block to import lib folder


from syncloud_files.web import create_web_app
app = create_web_app(app_path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)