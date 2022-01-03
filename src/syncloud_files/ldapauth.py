import ldap


def authenticate(name, password):
    conn = ldap.initialize('ldap://localhost:389')
    try:
        conn.simple_bind_s('cn={0},ou=users,dc=syncloud,dc=org'.format(name), password)
    except Exception as e:
        conn.unbind()
        if 'desc' in e.message:
            raise Exception(e.message['desc'])
        else:
            raise Exception(e.message)
