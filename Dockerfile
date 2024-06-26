FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && apt install -y curl && curl -fsSL https://deb.nodesource.com/setup_22.x | bash -

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libxml2-dev libxslt-dev zlib1g-dev apache2 libgdbm-dev liblz4-tool brotli ripgrep gcc make python3-dev wget sudo nodejs python3.10-venv && \
    apt-get clean && rm -rf /var/lib/apt

# Install pip
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py

# Install PhiloLogic
COPY . /PhiloLogic4
WORKDIR /PhiloLogic4
RUN sh install.sh && mkdir /var/www/html/philologic

RUN a2enmod rewrite && a2enmod cgi && a2enmod brotli


# Configure global variables
RUN sed -i 's/database_root = None/database_root = "\/var\/www\/html\/philologic\/"/' /etc/philologic/philologic4.cfg && \
    sed -i 's/url_root = None/url_root = "http:\/\/localhost\/philologic\/"/' /etc/philologic/philologic4.cfg

RUN echo "#!/bin/bash\nservice apache2 stop\nrm /var/run/apache2/*\napachectl -D FOREGROUND" > /autostart.sh && chmod +x /autostart.sh

# Set up Apache
RUN perl -i -p0e 's/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride None/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride all/smg' /etc/apache2/apache2.conf
EXPOSE 80
CMD ["/autostart.sh"]