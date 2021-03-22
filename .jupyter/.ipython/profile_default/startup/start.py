import logging
import os
import sys

import const
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from tqdm import tqdm

sys.path.append("/home/contuser1/project/module")


plt.style.use(["fivethirtyeight"])

# not use gpu
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""


# set log
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"
fmt = const.LOG_FORMAT
# set timezone
logging.Formatter.converter = const.LOG_JP_TZ
logging.basicConfig(
    level=logging.DEBUG,
    format=fmt,
    filemode="w",
    filename=f"{const.LOG_DIR}/jupyter.log",
)
console = logging.StreamHandler()
console_formatter = logging.Formatter(fmt)
console.setFormatter(console_formatter)
console.setLevel(logging.INFO)
logging.getLogger(__name__).addHandler(console)
logging.getLogger("module").addHandler(console)
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
