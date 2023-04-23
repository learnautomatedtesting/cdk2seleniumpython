FROM selenium/hub:4.8.3-20230404

USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        unzip \
        wget \
        xvfb

USER seluser