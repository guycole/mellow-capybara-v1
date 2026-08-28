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

# Require wombat UID/GID to be provided by the Linux build host.
ARG WOMBAT_UID
ARG WOMBAT_GID

RUN set -eux; \
	test -n "${WOMBAT_UID}"; \
	test -n "${WOMBAT_GID}"

RUN printf '%s\n' '#!/bin/sh' 'set -eu' \
	'uid="${WOMBAT_UID:?WOMBAT_UID is required}"' \
	'gid="${WOMBAT_GID:?WOMBAT_GID is required}"' \
	'printf "WOMBAT_UID=%s\nWOMBAT_GID=%s\n" "$uid" "$gid" > /app/wombat_env.env' \
	> /usr/local/bin/collect-wombat-ids.sh \
	&& chmod +x /usr/local/bin/collect-wombat-ids.sh

ENV WOMBAT_UID=${WOMBAT_UID}
ENV WOMBAT_GID=${WOMBAT_GID}

RUN /usr/local/bin/collect-wombat-ids.sh

# Create and activate virtualenv first
RUN python -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements and install them inside the venv
COPY wombat_docker/requirements.txt ./
RUN $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

COPY helper/ ./helper/
COPY wombat_docker/capybara_app.py ./
COPY wombat_docker/validator.py ./

RUN printf '%s\n' '#!/bin/sh' 'set -e' '/usr/local/bin/collect-wombat-ids.sh' 'set -a' '[ -f /app/wombat_env.env ] && . /app/wombat_env.env' 'set +a' 'exec "$@"' > /usr/local/bin/docker-entrypoint.sh \
	&& chmod +x /usr/local/bin/docker-entrypoint.sh

ENV FAILURE_DIR=/mnt/wombat/failure
ENV FRESH_DIR=/mnt/wombat/fresh/capybara
ENV SUCCESS_DIR=/mnt/wombat/capybara/success

ENV DB_CONN=postgresql+psycopg2://capybara_client:batabat@172.17.0.1:5432/capybara

RUN mkdir -p /mnt/wombat
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "capybara_app.py"]
