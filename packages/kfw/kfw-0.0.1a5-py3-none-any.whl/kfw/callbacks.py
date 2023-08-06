import os
import pickle

import keras.callbacks as callbacks


class History(callbacks.History):
    def __init__(self, previous_history=None, file=None):
        super(History, self).__init__()
        self.prev_hist = previous_history
        self.file = file
        self.epoch = None
        self.history = None

    def on_train_begin(self, logs=None):
        # override the keras.callbacks.History method
        self.epoch = [] if self.prev_hist is None else self.prev_hist.epoch
        self.history = {} if self.prev_hist is None else self.prev_hist.history

    def on_train_end(self, logs=None):
        if self.file is None:
            return

        with open(self.file, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle_file(cls, file=None):

        if file is None or not os.path.exists(file):
            return cls(file=file)

        with open(file, 'rb') as f:
            history = pickle.load(f)
        return cls(history, file)
