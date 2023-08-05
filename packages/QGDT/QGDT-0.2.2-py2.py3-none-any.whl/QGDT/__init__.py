# -*- coding: utf-8 -*-
"""
努力不需要理由，如果需要，就是为了不需要的理由。
"""

__title__ = 'QGDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))

from QGDT.templates_init import x0_1,x0_2,x0_3
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
from .train_models import TrainRNN, TrainSVM, TrainW2V

__all__ = [Terms2Search,Search2Frequency,QGDT,QG,Search2Similar,
           chinese,device,embed_size,hidden_size,num_layers,num_epochs,batch_size,
           seq_length,learning_rate,log,get_current_path,jaccard,Dictionary,Corpus,
           RNNLM,extend_config,Configuration]


version_info = (0, 2, 2)

__version__ = ".".join(map(str, version_info))

print('__title__:',__title__)
print('__author__:',__author__)
print('__license__:',__license__)
print('__copyright__:',__copyright__)
print('__version__:',__version__)
print('__all__:',__all__)
