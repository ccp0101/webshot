FROM gliderlabs/herokuish
RUN apt-get update && apt-get install -y \
    xfonts-utils \
    cabextract \
    phantomjs \
 && rm -rf /var/lib/apt/lists/*

ADD dpkg-packages/ttf-mscorefonts-installer_3.6_all.deb /tmp/ttf-mscorefonts-installer_3.6_all.deb
RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections \
 && dpkg -i /tmp/ttf-mscorefonts-installer_3.6_all.deb \
 && rm /tmp/ttf-mscorefonts-installer_3.6_all.deb
