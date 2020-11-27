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

The Anonymization API is listening for HTTP POST requests on port **80** by default under the `/anonymize` path.
File in ***xml*** format should be passed via `--data-binary` option with content type set to  `application/octet-stream`.

You can test the API with cURL:

```console
$ curl -X POST --data-binary @<path_to_xml> -H "Content-Type: application/octet-stream" http://localhost:80/anonymize 
```

### Usage - Simple UI
Simple anonymization interface can be accessed via a web browser at http://localhost:80/

### Automatically start on system boot
To enable the automatic start of container on system boot, first run the container and then execute:

$ cp docker-anonymization.service /etc/systemd/system/
$ systemctl enable docker-anonymization.service
$ systemctl start docker-anonymization

To start/stop the container manually run:
$ systemctl start docker-anonymization
$ systemctl stop docker-anonymization
