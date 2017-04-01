from syncloud_files.web import create_web_app
app = create_web_app(app_path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)