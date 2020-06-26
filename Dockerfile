FROM jrottenberg/ffmpeg:ubuntu

# TODO: add hardware accelerated build as tag jrottenberg/ffmpeg:4.1-nvidia

RUN apt-get -y update && \
    apt-get install -y python-pip && \
    apt-get install -y python-opencv && \
    apt-get install -y git && \
    apt-get install wget
    
ENV APP_HOME /app
WORKDIR ${APP_HOME} 
 
ENV EXIFTOOL_VERSION=10.20
RUN cd /tmp \
	&& wget http://www.sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-${EXIFTOOL_VERSION}.tar.gz \
	&& tar -zxvf Image-ExifTool-${EXIFTOOL_VERSION}.tar.gz \
	&& cd Image-ExifTool-${EXIFTOOL_VERSION} \
	&& perl Makefile.PL \
	&& make test \
	&& make install \
	&& cd .. \
	&& rm -rf Image-ExifTool-${EXIFTOOL_VERSION}

ARG DOCKER_GID
ARG DOCKER_UID

# Add non-root user and fix permissions
RUN groupadd --gid $DOCKER_GID docker && adduser --uid $DOCKER_UID --gid $DOCKER_GID --disabled-password --quiet --gecos "" docker_user
COPY src/main/ /app
RUN chown -Rf docker_user:docker /app

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/app/extractor.py" ]
