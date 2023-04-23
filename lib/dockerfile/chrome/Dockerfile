FROM selenium/node-chrome:4.8.3-20230404

USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        unzip \
        wget \
        xvfb

# Download and install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q "https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/

USER seluser