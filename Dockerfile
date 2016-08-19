FROM python:3.4-slim
MAINTAINER Jason Kraus "zbyte64@gmail.com"


ENV HOME /root

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3-dev git-core gcc g++ make build-essential cmake pkg-config
#video components
RUN apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
                       libdc1394-22-dev libtheora-dev libvorbis-dev libxvidcore-dev \
                       libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libxine2-dev
#image components
RUN apt-get install -y libjpeg-dev libtiff-dev libjasper-dev libpng-dev \
                       libfreetype6-dev libgdal-dev libwebp-dev zlib1g-dev libopenexr-dev
#computation components
RUN apt-get install -y libatlas-base-dev gfortran libtbb-dev libeigen3-dev
RUN pip3 install --upgrade numpy theano lasagne matplotlib pillow scikit-learn imutils keras\
                           https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp34-cp34m-linux_x86_64.whl

RUN apt-get install -y wget unzip
ENV OPENCV_VERSION 3.0.0
RUN wget -q https://github.com/Itseez/opencv/archive/${OPENCV_VERSION}.zip -O opencv.zip && \
    unzip -q opencv.zip && mv /opencv-${OPENCV_VERSION} /opencv
RUN wget -q https://github.com/Itseez/opencv_contrib/archive/${OPENCV_VERSION}.zip -O opencv_contrib.zip && \
    unzip -q opencv_contrib.zip && mv /opencv_contrib-${OPENCV_VERSION} /opencv_contrib


WORKDIR /opencv
RUN mkdir build
WORKDIR /opencv/build
#RUN apt-get install -y libhdf5-dev libhdf5-serial-dev
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=OFF \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D WITH_IPP=OFF \
	-D WITH_V4L=ON \
  -D FORCE_VTK=ON \
  -D WITH_TBB=ON \
  -D WITH_GDAL=ON \
  -D WITH_XINE=ON \
	-D BUILD_EXAMPLES=OFF ..
RUN make -j2
RUN make install
RUN ldconfig
WORKDIR /usr/local/lib/python3.4/site-packages
RUN ln -s /usr/local/lib/python3.4/site-packages/cv2.cpython-34m.so cv2.so

WORKDIR $HOME

CMD python3
