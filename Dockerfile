FROM pytorch/pytorch:1.5-cuda10.1-cudnn7-runtime

COPY classla-stanfordnlp /usr/src/stanfordnlp
WORKDIR /usr/src/stanfordnlp

RUN pip install --no-cache-dir protobuf requests tqdm && \
    pip install --no-deps . && \
    apt-get update && apt-get install -y --no-install-recommends openjdk-11-jre openjdk-11-jdk

COPY Obeliks4J /usr/src/Obelisk4J
WORKDIR /usr/src/Obelisk4J

RUN javac -encoding UTF-8 src/main/java/org/obeliks/*.java -d target/classes && \
    cp src/main/resources/* target/classes/org/obeliks/ && \
    jar -cef org.obeliks.Tokenizer obeliks.jar -C target/classes org

RUN pip install --no-cache-dir flask gunicorn && \
    mkdir /pipeline
WORKDIR /pipeline
COPY pipeline_api.py wsgi.py /pipeline/

# TODO: Fix preloading. For now every worker loads its seperate models in memory.
CMD ["gunicorn", "--bind", "0.0.0.0:80", "-w", "1", "--timeout", "1800", "--access-logfile", "-",  "wsgi:app"]
