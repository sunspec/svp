## This is currently not working, please don't try this yet ##

FROM python:3.9.14

# Dockerfile author
MAINTAINER Jay Johnson (jjohns2@sandia.gov)

# update, install prerequisites, and add a user
# RUN apt-get update && apt-get upgrade -y 
# RUN apt install build-essential vim nano -y
RUN useradd -m -s /bin/bash svp_user
USER svp_user

# copy in the code
COPY * /home/svp_user/
WORKDIR /home/svp_user

RUN pip install wheel
RUN pip install attrdict
#RUN mkdir /home/svp_user/wheels
#RUN pip wheel --wheel-dir=/home/svp_user/wheels --requirement /home/svp_user/svp_requirements.txt
RUN pip install --no-cache-dir -r /home/svp_user/svp_requirements.txt

CMD [ "python", "./ui.py" ]
