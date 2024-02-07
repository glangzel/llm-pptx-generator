# set base image (host OS)
FROM python:3.10-bookworm

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt /code
COPY pip.conf /etc/pip.conf

# install dependencies
RUN apt update
RUN apt install sqlite3 
RUN pip install pip --upgrade
RUN pip install -r "requirements.txt"
COPY requirements2.txt /code
RUN pip install -r "requirements2.txt"
RUN rm /etc/pip.conf 

# Copy local libraries
COPY src/ /code
COPY ollama_aicore/ /code/ollama_aicore
COPY img/ /code/img
COPY settings/ /code/settings

# expose a port for Gradio
EXPOSE 5110



# command to run on container start
CMD [ "/bin/bash" ]