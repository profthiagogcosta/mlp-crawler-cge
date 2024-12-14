# REF: https://github.com/nazliander/scrape-nr-of-deaths-istanbul/blob/master/Dockerfile
ARG PYTHON_IMAGE_VERSION="3.9"

FROM python:${PYTHON_IMAGE_VERSION}

#------------------------------
# DESC: INFORMATIONS ABOUT THE PROCESS
# TO SCRAPPING THE SITE OF THE CGE-SP

ARG DATA_INFERIOR="28/10/2019"
ENV DATA_INFERIOR=${DATA_INFERIOR}

ARG DATA_SUPERIOR="28/10/2019"
ENV DATA_SUPERIOR=${DATA_SUPERIOR}
#------------------------------

#------------------------------
# DESC: MONGODB CONFIGS

ARG MONGODB_USER='root'
ENV MONGODB_USER=${MONGODB_USER}

ARG MONGODB_PASSWORD='password'
ENV MONGODB_PASSWORD=${MONGODB_PASSWORD}

ARG MONGODB_HOST='localhost'
ENV MONGODB_HOST=${MONGODB_HOST}

ARG MONGODB_PORT='27017'
ENV MONGODB_PORT=${MONGODB_PORT}

#------------------------------

#------------------------------
# DESC: MONGODB CONFIGS

ARG API_CODE='AIzaSyBo9Fo14Zs3mMCGENkW3aOFVj1fdWGei14'
ENV API_CODE=${API_CODE}

ARG SCRAPPING_LEVEL='silver'
ENV SCRAPPING_LEVEL=${SCRAPPING_LEVEL}

#------------------------------

WORKDIR /mlp-crawler-cge

RUN chmod -R 775 ./

ENV PYTHONPATH="/mlp-crawler-cge"

COPY pyproject.toml poetry.lock ./

# DESC: Install the poetry, set the env var in the project directory,
# and install the dependencies

RUN python -m pip install -q poetry==1.8.3 \
    && python -m poetry config virtualenvs.in-project true \
    && python -m poetry install --only main

COPY /scripts ./scripts

COPY /src ./src

#-------------------------
# DESC: only for debugging on the development process
# RUN python -m poetry run python /mlp-crawler-cge/scripts/get_floods.py
# ENTRYPOINT ["tail", "-f", "/dev/null"]
#-------------------------

CMD ["python", "-m", "poetry", "run", "python", "/mlp-crawler-cge/scripts/get_floods.py"]

#----------INSTRUCTIONS----------

# buildar a imagem
#docker build -t scientific_crawler .

# executar o container com os containers visualizando a rede da maquina
#docker run -d --name crawler_cge_service --network host crawler_cge

# acessar o container
#docker exec -i -t crawler_cge_service bash

# finalizar a execucao do container
#docker kill crawler_cge_service

# excluir os containers finalizados
#docker rm $(docker ps -a -q)
