# from base image
FROM continuumio/miniconda3
# maintainer
LABEL maintainer="alexadra.skyslakova@gmail.com"
# install packages
RUN conda install -y bokeh flask
# set the working directory to /app
WORKDIR /app
# copy the current directory contents into the working directory
COPY . /app
# install requirements for the app
RUN pip install -r requirements.txt
# make port 5006 avaiable to the world outside the container
EXPOSE 5006
EXPOSE 8000
# run bokeh serve whem container launches
CMD python -m app