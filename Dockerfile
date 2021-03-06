ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}-alpine

ARG POETRY_VERSION=1.1.9

RUN pip install --upgrade pip

RUN apk add --no-cache \
        curl \
        build-base \
        libressl-dev \
        musl-dev \
        libffi-dev \
        libxslt-dev \
        libxml2 \
        git \
        nginx \
        apache2-utils && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile=minimal && \
    source $HOME/.cargo/env && \
    pip install --no-cache-dir poetry==${POETRY_VERSION}

RUN mkdir -p /app /etc/chaperone.d
WORKDIR /app

RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock /app/
RUN source $HOME/.cargo/env && poetry install -n --no-ansi --no-dev
# Poetry breaks itself here...
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

RUN apk del \
        curl \
        libressl-dev \
        musl-dev \
        libffi-dev \
        libxml2 \
        git
RUN rm -r /root/.rustup
RUN yes | poetry cache clear . --all

COPY . /app
COPY chaperone.conf /etc/chaperone.d/
COPY nginx.conf /etc/nginx/http.d/default.conf

CMD ["poetry", "run", "chaperone"]
