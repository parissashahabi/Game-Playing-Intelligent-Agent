# change_it
from logics.actions import Actions
import pandas as pd

GEM_SCORES = [50, 100, 200, 300]

HIT_HURT = -20
BARBED_HURT = -20
STRAIGHT_MOVE_HURT = -1
DIAGONAL_MOVE_HURT = -2

GEM_SEQUENCE_SCORE = [
    [50, 0, 0, 0],
    [50, 200, 100, 0],
    [100, 50, 200, 100],
    [50, 100, 50, 200],
    [250, 50, 100, 50]

]

PROBABILITIES = {}


def update_probabilities(xlsx_file_path):
    global PROBABILITIES
    result = {}
    for cell_type in ["normal", "slider", "barbed", "teleport"]:
        df = pd.read_excel(xlsx_file_path, sheet_name=cell_type)
        df.index = df[df.columns[0]]
        df.drop(df.columns[0], axis=1, inplace=True)
        result[cell_type] = df.transpose().to_dict()
    PROBABILITIES = result
#
#
# PROBABILITIES = {
#     "normal": {
#         "real_action": 0.8,
#         "option1": 0.1,
#         "option2": 0.1
#
#     },
#     "slider": {
#         "real_action": 0.4,
#         "option1": 0.3,
#         "option2": 0.3
#
#     },
#     "barbed": {
#         Actions.NOOP: 0.5,
#         "real_action": 0.3,
#         "option1": 0.1,
#         "option2": 0.1
#     },
#     "teleport": {
#         Actions.TELEPORT: 0.5,
#         "real_action": 0.5
#
#     }
# }
