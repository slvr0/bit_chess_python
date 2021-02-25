
from keras.models import Sequential
from keras.layers import Dense,Input
import numpy as np
import os
from tensorflow.keras.models import load_model,save_model

class KerasNet :
  def __init__(self, input_dims, output_dims,net_name="default"):
    self.model = Sequential()
    self.model.add(Input(shape=input_dims))
    self.model.add(Dense(4, activation='relu'))
    self.model.add(Dense(4, activation='relu'))
    self.model.add(Dense(output_dims, activation='sigmoid'))
    self.model.compile(loss='mse', optimizer='adam')

    self.fp = os.path.join('models', net_name)

  def train_on_batch(self, input, output_correct):
    self.model.train_on_batch(input, output_correct)

  def test_on_batch(self, input, output_correct):
    return self.model.test_on_batch(input, output_correct)

  def save_model(self):
    save_model(self.model, self.fp)

  def predict(self, state):

    return self.model.predict(np.expand_dims(state, axis=0))

  def fit(self, input, output_correct, test_freq = 0, callback = []):
    self.model.fit(input, output_correct,validation_split = test_freq, callbacks=[callback])

  def load_model(self, load_from = ""):
    if os.path.isdir(self.fp) :
      self.model = load_model(self.fp)
      print("loaded model @ {}".format(self.fp))
    else :
      print("found no model to load (KerasNet")
