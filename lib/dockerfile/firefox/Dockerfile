FROM selenium/node-firefox:4.8.3-20230404

USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        unzip \
        wget \
        xvfb

# Download and install geckodriver
RUN GECKODRIVER_VERSION=$(curl -sS https://github.com/mozilla/geckodriver/releases/latest | grep -oP 'v\K.*\d') && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar xf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/

USER seluser