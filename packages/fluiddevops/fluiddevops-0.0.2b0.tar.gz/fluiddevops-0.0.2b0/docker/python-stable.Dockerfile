FROM python:2.7
MAINTAINER Ashwin Vishnu Mohanan <avmo@kth.se>

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY apt_requirements.txt /usr/src/app/
RUN apt-get update
RUN apt-get install -y --no-install-recommends $(grep -vE "^\s*#" apt_requirements.txt  | tr "\n" " ")
# RUN apt-get install -y --no-install-recommends python python-pip python-dev

# RUN ./install_python.sh 3.6.0 9.0.1
ENV PYTHON_VERSION 3.6.0
ENV PYVER 3
ENV PYTHON_PIP_VERSION 9.0.1
RUN set -ex \
	&& if [ "$PYVER" -eq "2" ]; then \
	    FLAGS='--enable-shared --enable-unicode=ucs4' \
	; else \
	    FLAGS='--enable-loadable-sqlite-extensions --enable-shared --enable-optimizations' \
	; fi \
        && buildDeps='tcl-dev tk-dev' \
	&& apt-get update && apt-get install -y $buildDeps --no-install-recommends && rm -rf /var/lib/apt/lists/* \
	\
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	\
	&& cd /usr/src/python \
	&& ./configure --prefix=/usr $FLAGS \
	&& make -j$(nproc) \
	&& make install \
	&& ldconfig \
	\
	&& if [ ! -e /usr/local/bin/pip$PYVER ]; then : \
		&& wget -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
		&& python$PYVER /tmp/get-pip.py "pip==$PYTHON_PIP_VERSION" \
		&& rm /tmp/get-pip.py \
	; fi \
	&& pip$PYVER install --no-cache-dir --upgrade --force-reinstall "pip==$PYTHON_PIP_VERSION" \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a -name test -o -name tests \) \
			-o \
			\( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		\) -exec rm -rf '{}' + \
        && apt-get purge -y --auto-remove $buildDeps \
	&& rm -rf /usr/src/python ~/.cache

RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -U -r requirements.txt
RUN pip3 install --no-cache-dir -U -r requirements.txt
COPY requirements_extra.txt /usr/src/app/
RUN pip install --no-cache-dir -U -r requirements_extra.txt
RUN pip3 install --no-cache-dir -U -r requirements_extra.txt
COPY . /usr/src/app

RUN mkdir -p /root/.config/matplotlib \
	&&  echo 'backend      : agg' > /root/.config/matplotlib/matplotlibrc
