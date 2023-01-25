FROM ubuntu:22.04

CMD ["/bin/bash"]

# Install dependencies
RUN apt-get update && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libxml2-dev libxslt-dev zlib1g-dev apache2 libgdbm-dev python3-pip liblz4-tool brotli gcc make python3-dev wget sudo && \
    apt-get clean && rm -rf /var/lib/apt

# Install PhiloLogic
RUN wget https://github.com/ARTFL-Project/PhiloLogic4/archive/refs/tags/v4.7.3.4.tar.gz -O philologic.tar.gz
RUN mkdir PhiloLogic4 && tar -xf philologic.tar.gz -C PhiloLogic4 --strip-components=1 && \
    cd PhiloLogic4 && sh install.sh && \
    a2enmod rewrite && a2enmod cgi && a2enmod brotli

# Configure global variables
RUN sed -i 's/database_root = None/database_root = "\/var\/www\/html\/philologic\/"/' /etc/philologic/philologic4.cfg && \
    sed -i 's/url_root = None/url_root = "http:\/\/localhost\/philologic\/"/' /etc/philologic/philologic4.cfg

RUN echo "#!/bin/bash\nservice apache2 stop\nrm /var/run/apache2/*\napachectl -D FOREGROUND" > /autostart.sh && chmod +x /autostart.sh

# Set up Apache
RUN perl -i -p0e 's/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride None/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride all/smg' /etc/apache2/apache2.conf
EXPOSE 80
CMD ["/autostart.sh"]