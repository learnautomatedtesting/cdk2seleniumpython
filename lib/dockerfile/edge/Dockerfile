FROM selenium/node-edge:4.8.3-20230404
USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        unzip \
        wget \
        xvfb

# Download and install the Microsoft Edge Driver
RUN wget -q "https://msedgedriver.azureedge.net/latest/edgedriver_linux64.zip" && \
    unzip edgedriver_linux64.zip && \
    rm edgedriver_linux64.zip && \
    mv msedgedriver /usr/local/bin/

USER seluser