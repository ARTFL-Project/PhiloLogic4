# Use latest Ubuntu LTS
FROM ubuntu:20.04

# Download and install PhiloLogic with all associated dependencies
RUN apt-get update && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libxml2-dev libxslt-dev zlib1g-dev apache2 libgdbm-dev gcc make python3-dev python3-pip liblz4-tool curl sudo && \
    apt-get clean && rm -rf /var/lib/apt &&\
    mkdir philologic &&  \
    curl -L $(curl -s https://api.github.com/repos/ARTFL-Project/philologic4/releases/latest | grep tarball_url | cut -d '"' -f 4) | tar xvz -C philologic --strip-components 1 && \
    cd philologic && sh install.sh && \
    a2enmod rewrite && a2enmod cgi

RUN sed -i 's/database_root = None/database_root = "\/var\/www\/html\/philologic\/"/' /etc/philologic/philologic4.cfg && \
    sed -i 's/url_root = None/url_root = "http:\/\/localhost\/philologic\/"/' /etc/philologic/philologic4.cfg && \
    perl -i -p0e 's/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride None/<Directory \/var\/www\/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride all/smg' /etc/apache2/apache2.conf


# Port open
EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]