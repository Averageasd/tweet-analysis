FROM apache/airflow:3.1.2

USER root

# Install compiler for pycld2 and spatial libs for geopandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Pre-download NLTK data so it's ready when the container starts
RUN python -m nltk.downloader vader_lexicon punkt_tab wordnet omw-1.4 averaged_perceptron_tagger_eng