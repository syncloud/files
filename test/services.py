import time

SERVICES = ['filebrowser', 'nginx']


def wait_for_socket(device, app):
    path = '/var/snap/{0}/current/filebrowser.sock'.format(app)
    kind = ''
    for _ in range(60):
        kind = device.run_ssh('stat -c %F {0}'.format(path), throw=False).strip()
        if kind == 'socket':
            return
        time.sleep(5)
    raise AssertionError('{0} is not a socket after 5 minutes: {1}'.format(path, kind))


def assert_no_restarts(device, app):
    for service in SERVICES:
        restarts = device.run_ssh('systemctl show -p NRestarts --value snap.{0}.{1}.service'.format(app, service))
        assert restarts.strip() == '0', '{0}.{1} was restarted {2} times'.format(app, service, restarts.strip())
