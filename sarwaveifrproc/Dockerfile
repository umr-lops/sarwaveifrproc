FROM nvcr.io/nvidia/tensorflow:24.02-tf2-py3
#FROM nvcr.io/nvidia/tensorflow:23.07-tf2-py3
#FROM nvcr.io/nvidia/tensorflow:22.12-tf2-py3
RUN pip install xarray
RUN pip install tqdm
RUN pip install numpy
RUN apt install -y git
#RUN pip install git+https://github.com/umr-lops/sarwaveifrproc.git
#RUN pip install https://github.com/umr-lops/sarwaveifrproc.git==2024.4.9.post1
#RUN pip install sarwaveifrproc==2024.4.9.post1
RUN pip install git+https://github.com/umr-lops/sarwaveifrproc.git@main
#RUN pip install git+https://github.com/umr-lops/sarwaveifrproc.git@fix_log_and_workflow
#RUN pip install git+https://github.com/umr-lops/sarwaveifrproc.git@main
#RUN pip install git+https://github.com/umr-lops/sarwaveifrproc.git@dev
#COPY localconfig.yaml /usr/local/lib/python3.10/dist-packages/sarwaveifrproc/localconfig.yaml
