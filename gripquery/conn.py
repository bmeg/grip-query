import gripql

GRIP="http://localhost:8201"
CRED=None


def connect():
    return gripql.Connection(GRIP, credential_file=CRED)
