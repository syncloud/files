from os.path import join, dirname, abspath
from syncloud_files.web import create_web_app

app_path = abspath(join(dirname(__file__), '..'))
app = create_web_app(app_path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)