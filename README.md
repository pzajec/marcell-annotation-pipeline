# Deploying

## How do I get the model files?
Run `get-models.sh` or get them yourself from [clarin.si](https://www.clarin.si/repository/xmlui/).

## Docker

### Building
Build the Docker image:

```console
$ ./build.sh
```

### Deploying
Run with docker-compose:

```console
$ docker-compose up -d
```

### Usage - Anonymization API

The Anonymization API is listening for HTTP POST requests on port **5000** by default under the `/anonymize` path.
File in ***xml*** format should be passed via `--data-binary` option with content type set to  `application/octet-stream`.

You can test the API with cURL:

```console
$ curl -X POST --data-binary @<path_to_xml> -H "Content-Type: application/octet-stream" http://localhost:5000/anonymize 
```

### Usage - Simple UI
Simple anonymization interface can be accessed via a web browser at http://localhost:5000/


