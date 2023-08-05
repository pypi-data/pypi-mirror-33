#!/bin/bash

export PYTHON_VERSION=$1
export PYVER=${1:0:1}
export PYTHON_PIP_VERSION=$2

if [ "$PYVER" -eq "2" ]; then
    FLAGS='--enable-shared
           --enable-unicode=ucs4'
else
    FLAGS='--enable-loadable-sqlite-extensions
           --enable-shared
           --enable-optimizations'
fi

set -ex \
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
