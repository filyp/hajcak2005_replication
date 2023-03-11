FROM filyp/psychopy:latest

# RUN git clone --recurse-submodules https://github.com/filyp/hajcak2005_replication.git

ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt

WORKDIR /hajcak2005_replication
ENTRYPOINT [ "python3", "main.py"]
CMD [ "config/flankers_hajcak2005_with_cues_short_notrig.yaml" ]

