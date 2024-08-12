FROM nvidia/cuda:11.8.0-devel-ubuntu22.04 as base

RUN chsh -s /bin/bash
SHELL ["/bin/bash", "-c"]

ARG UID
ARG GID

WORKDIR /reranker

RUN mkdir /home/myuser \
    && groupadd --gid $GID myuser \
    && useradd --home /home/myuser -u $UID --gid $GID myuser -s /bin/bash \
    && chown -R myuser /reranker /home/myuser

RUN apt-get -q update \
    && apt-get install -q -y wget git openjdk-11-jdk

USER myuser

RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/home/myuser/miniconda3/bin:${PATH}"
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY tools/reranker/environment.yml /reranker/environment.yml

RUN conda env create -f environment.yml \
    && conda clean --all --force-pkgs-dirs --yes

FROM base

COPY tools/reranker/rerank.py /reranker/rerank.py

ENV PATH="/home/myuser/miniconda3/envs/reranker/bin/:${PATH}"
