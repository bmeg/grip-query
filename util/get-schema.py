
import json
import gripql

GRIP="https://bmeg.io"
CRED="bmeg_credentials.json"
graph="rc5"


G = gripql.Graph(GRIP, credential_file=CRED, graph=graph)
schema = G.getSchema()

print(json.dumps(schema))
