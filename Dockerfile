FROM python:3.8-slim as stage0

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gcc \
        libsasl2-dev \
        libldap2-dev \
        libssl-dev \
        graphviz \
        libgraphviz-dev \
        libpq-dev \
        make \
 && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml pyproject.toml
COPY poetry.lock poerty.lock

RUN pip install --no-compile --upgrade pip \
 && pip install --no-compile poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi \
 && pip uninstall --yes poetry

COPY ./src /src

RUN pip install --no-compile poetry && poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi \
 && pip uninstall --yes poetry

# --------------- unit tests and linters --------------
#from stage0 as test
#RUN pip3 install pytest==5.3.1 mypy==0.790 pylint==2.6.0
## mypy пока запускаем без конфигурации, посмотрим, что не будет нравится в дефолте - поменяем
#COPY pylintrc pylintrc
#COPY mypy.ini mypy.ini
#RUN pylint --rcfile pylintrc /src
#RUN mypy /src --config-file mypy.ini


# --------------- final image --------------
FROM stage0 as final
ENTRYPOINT [""]
CMD ["python3", "-m", "src.main"]
