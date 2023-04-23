FROM selenium/node-firefox:4.8.3-20230404

USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        unzip \
        wget \
        xvfb

# Download and install geckodriver
RUN GECKODRIVER_VERSION=$(curl --silent https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar xf geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz && \
    rm geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/

USER seluser