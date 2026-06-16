# Code-sandbox base image. The backend can shell out to this image (or run
# subprocess sandboxes directly). Provides Python + Node runtimes with no
# network by default when run with --network none.
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# non-root user for executing untrusted code
RUN useradd -m sandboxuser
USER sandboxuser
WORKDIR /sandbox

CMD ["python", "-c", "print('agentflow sandbox image')"]
