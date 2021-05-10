
# GRIP Query UI


# Example server

## Setting up Grip

```
grip server
```

## Setting up example GDC graph

Download GDC data
```
./example/download-gdc-cases.py
```

Create GDC graph
```
grip create gdc
```

Load GDC graph data
```
grip load gdc --vertex TCGA-BRCA.json.vertices --edge TCGA-BRCA.json.edges
```

Sample graph to get schema
```
grip schema sample gdc > schema.json
```

Load Schema into server
```
grip schema post --json schema.json
```

## Turning on GripQuery web UI
Launch grip server
```
python -m gripquery
```

The web UI should now be avalible at http://localhost:8050

# Connecting to BMEG.io server
To connect server against BMEG.io, get `bmeg_credentials.json` file from [BMEG](https://bmeg.io/analyze/access)

Start server with command
```
python -m gripquery --port 8060 --grip https://bmeg.io --cred bmeg_credentials.json
```
