# -*- coding: utf-8 -*-
"""
努力不需要理由，如果需要，就是为了不需要的理由。
"""

__title__ = 'QGDT-cpu'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))

from QGDT.correlation_calculate import Terms2Search
from QGDT.frequency_calculate import Search2Frequency
from QGDT.qgdt import QGDT
from QGDT.question_generate import QG
from QGDT.similarity_calculate import Search2Similar
from QGDT.tools import (chinese,
                        device,
                        embed_size,
                        hidden_size,
                        num_layers,
                        num_epochs,
                        batch_size,
                        seq_length,
                        learning_rate,
                        log,
                        get_current_path,
                        jaccard,
                        Dictionary,
                        Corpus,
                        RNNLM,
                        extend_config,
                        Configuration, )
from QGDT.train_models import TrainRNN, TrainSVM, TrainW2V
from QGDT.templates_x import templates_x1,templates_x2,templates_x3

version_info = (0, 3, 3)

__version__ = ".".join(map(str, version_info))

print('__title__:',__title__)
print('__author__:',__author__)
print('__license__:',__license__)
print('__copyright__:',__copyright__)
print('__version__:',__version__)
