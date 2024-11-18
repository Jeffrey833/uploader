#!/bin/bash
# Compile and install (or install via Apt) FFmpeg Codecs
# Compile and install FFmpeg suite

echo "Begining Installation of FFmpeg Suite"

#Update APT Repository
echo "Updating the APT repository information"
apt-get update

#Create Working Directories
echo "Setting up working directories to be used during the installation and build process"
cd ~
mkdir ~/ffmpeg_sources
mkdir ~/ffmpeg_build
#Build Tools
echo "Installing various tools and packages, including audio-video codecs, required for building FFmpeg"
apt-get -y install autoconf automake build-essential libass-dev libfreetype6-dev \
  libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
  libxcb-xfixes0-dev pkg-config texinfo zlib1g-dev
 #YASM Assembler
echo "Installing the YASM Assembler"
apt-get install -y yasm

echo "Compiling and Installing FFmpeg Codecs"

#x264 Codec
echo "X264 Codec"
cd /home/pi/ffmpeg_sources
git clone git://git.videolan.org/x264
cd x264
./configure --host=arm-unknown-linux-gnueabi --enable-shared --disable-opencl
make -j2
make install
make clean
make distclean
 echo "Libfdk-aac Codec"
cd ~/ffmpeg_sources
wget -O fdk-aac.tar.gz https://github.com/mstorsjo/fdk-aac/tarball/master
tar xzvf fdk-aac.tar.gz
cd mstorsjo-fdk-aac*
autoreconf -fiv
./configure  --enable-shared
make -j2
make install
make clean
make distclean
 #Libmp3lame Codec 
echo "Libmp3lame Codec"
apt-get install -y libmp3lame-dev

#Libopus Codec
echo "Libopus Codec"
apt-get install -y libopus-dev

#Libvpx Codec
echo "Libvpx Codec"
cd ~/ffmpeg_sources
wget http://storage.googleapis.com/downloads.webmproject.org/releases/webm/libvpx-1.5.0.tar.bz2
tar xjvf libvpx-1.5.0.tar.bz2
cd libvpx-1.5.0
PATH="$HOME/bin:$PATH" ./configure --enable-shared --disable-examples --disable-unit-tests
PATH="$HOME/bin:$PATH" make -j2
make install
make clean
make distclean
 # FFmpeg Suite
echo "Compiling and installing the FFmpeg Suite"
cd ~/ffmpeg_sources
wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg

PATH="$HOME/bin:$PATH" ./configure \
  --pkg-config-flags="--static" \
  --extra-cflags="-fPIC -I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-nonfree \
  --enable-pic \
  --extra-ldexeflags=-pie \
  --enable-shared

PATH="$HOME/bin:$PATH" make -j2
make install
make distclean
hash -r

#Update Shared Library Cache
echo "Updating Shared Library Cache"
ldconfig

echo "FFmpeg and Codec Installation Complete"
