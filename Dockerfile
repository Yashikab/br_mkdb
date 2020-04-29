FROM yashikab/jupyter-gpu

LABEL Yashio Kabashima

# lab extention
RUN jupyter labextension install @mohirio/jupyterlab-horizon-theme
RUN jupyter labextension install @hokyjack/jupyterlab-monokai-plus
RUN jupyter labextension install @lckr/jupyterlab_variableinspector
RUN jupyter labextension install @jupyterlab/toc
