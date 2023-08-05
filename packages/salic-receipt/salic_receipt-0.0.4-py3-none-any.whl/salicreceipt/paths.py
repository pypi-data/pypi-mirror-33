import os
import sys

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

DATA_PATH = os.path.join(FILE_PATH, 'data')
DATA_CSV_PATH = os.path.join(DATA_PATH, 'csv')
DATA_PICKLE_PATH = os.path.join(DATA_PATH, 'pickle')
RECEIPTS_CSV_PATH = os.path.join(DATA_CSV_PATH, 'comprovantes_pagamento.csv')
RECEIPTS_PICKLE_PATH = os.path.join(DATA_PICKLE_PATH,
                                    'id_arquivos.pickle')
