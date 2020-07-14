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

or manually:

```console
$ docker run --name obeliks4j-classla-stanfordnlp -d \
    -p 127.0.0.1:5000:80 \
    obeliks4j-classla-stanfordnlp:latest
```

### GPU support
To enable Docker GPU support on your host, please refer to the [Nvidia docs](https://developer.nvidia.com/nvidia-container-runtime).
Once you have nvidia-container-runtime set up, you can add the folowing runtime definition to `/etc/docker/daemon.json`:

```json
{
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

and uncomment lines containing `nvidia` in `docker-compose.yml`.


# Usage

The API is listening for HTTP POST requests under the `/annotate` path containing the following form data:
    - "text": raw text data
    - "meta": standoff metadata in JSON format

An example of standoff metadata:

```json
{
    "doc_id":"sl-test123",
    "language":"sl",
    "date":"2020-06-30",
    "title":"Poskusni dokument",
    "type":"poskus",
    "entype":"test"
}
```

You can test the API with cURL:

```console
$ curl -X POST -F 'text=Pozdravljen, svet!' -F 'meta={"doc_id":"sl-test123", "language":"sl", "date":"2020-06-30", "title":"Poskusni dokument", "type":"poskus", "entype":"test"}' http://localhost:5000/annotate 
```


# Issues

- Preloading with Gunicorn doesn't work yet. Thus every worker has to load the whole pipeline separately in memory, instead of just using one instance.
