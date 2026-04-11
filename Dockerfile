FROM apache/airflow:3.1.2

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

ENV NLTK_DATA=/home/airflow/nltk_data

RUN pip install --no-cache-dir \
    pandas \
    pycld2 \
    nltk \
    apache-airflow-providers-google \
    pyarrow

RUN python -m nltk.downloader -d $NLTK_DATA vader_lexicon \
    punkt_tab \
    wordnet \
    omw-1.4 \
    averaged_perceptron_tagger_eng