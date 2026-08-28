# Linux hosts only — must be built on a Linux host where the wombat user exists.
#
# docker build --build-arg WOMBAT_UID=$(id -u wombat) --build-arg WOMBAT_GID=$(id -g wombat) -t capybara:latest .
# docker run -v /var/wombat:/mnt/wombat --name capybara capybara:latest
# docker run -e stuntbox=validate -v /var/wombat:/mnt/wombat --name capybara capybara:latest
# docker run -e stuntbox=score -e limit=5 --name capybara capybara:latest
# docker run -e stuntbox=score --name capybara capybara:latest
#
FROM python:3.11-slim

WORKDIR /app

# Create and activate virtualenv first
RUN python -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements and install them inside the venv
COPY peccary_docker/requirements.txt ./
RUN $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

COPY helper/ ./helper/
COPY peccary_docker/capybara_app.py ./
COPY peccary_docker/loader.py ./

RUN printf '%s\n' '#!/bin/sh' 'set -e' 'exec "$@"' > /usr/local/bin/docker-entrypoint.sh \
	&& chmod +x /usr/local/bin/docker-entrypoint.sh

ENV FAILURE_DIR=/mnt/peccary/capybara/failure
ENV FRESH_DIR=/mnt/peccary/capybara/capybara-v1

# On Linux (production): override with -e DB_CONN=...@172.17.0.1:5432/capybara
# On macOS (Docker Desktop): host.docker.internal resolves to the host machine
ENV DB_CONN=postgresql+psycopg2://capybara_client:batabat@host.docker.internal:5432/capybara

RUN mkdir -p /mnt/peccary
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "capybara_app.py"]
