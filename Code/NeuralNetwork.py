#!/usr/bin/env python
# coding: utf-8

# In[87]:


from __future__ import absolute_import, division, print_function

import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print(tf.__version__)


# Data Wrangling

# In[88]:


#open data
df = pd.read_csv('MergedData.csv')
#drop unessisary data
df.drop(columns = ['Unnamed: 0','CensusTract','lng','lat','x','y','geoid','field_1'], inplace = True)

#one-hot encode bed (1-5), bath(1-5 with 1/2 steps no 4.5), type(apartment, condo, duplex, house, townhouse), and UrbanType (urban_area, urban_cluster)
temp0 = pd.get_dummies(df.bed, 'bed')
temp1 = pd.get_dummies(df.bath, 'bath')
temp2 = pd.get_dummies(df.type, 'type')
temp3 = pd.get_dummies(df.UrbanType, 'UrbanType')

merge = pd.concat([temp0, temp1, temp2, temp3], axis = 1)
df = pd.concat([df, merge], axis = 1)
df.drop(columns = ['bed', 'bath', 'type', 'UrbanType'], inplace = True)

#scale approprite data, sqrtft, and pop2010
min_max_scaler = MinMaxScaler()
df[['sqrtft', 'pop2010']] = MinMaxScaler().fit_transform(df[['sqrtft', 'pop2010']])
print(df)


# In[97]:


#split Data
train, test = train_test_split(df, test_size=.25)

#Assign Lable
train_lables = train.pop('price')
test_lables = test.pop('price')


# In[196]:


def build_model():
  model = keras.Sequential([
    layers.Dense(512, activation=tf.nn.relu, input_shape=[len(train.keys())]),
    layers.Dense(512, activation=tf.nn.relu),
    layers.Dense(256, activation=tf.nn.relu),
    layers.Dense(256, activation=tf.nn.relu),
    layers.Dense(128, activation=tf.nn.relu),
    layers.Dense(128, activation=tf.nn.relu),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(1)
  ])

  optimizer = tf.keras.optimizers.RMSprop(0.001)

  model.compile(loss='mean_squared_error',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mean_squared_error'])
  return model
model = build_model()
model.summary()


# In[158]:


# example_batch = train[:10]
# example_result = model.predict(example_batch)
# example_result


# In[197]:


# Display training progress by printing a single dot for each completed epoch
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

EPOCHS = 5000

history = model.fit(
  train, train_lables,
  epochs=EPOCHS, validation_split = 0.2, verbose=0,
  callbacks=[PrintDot()])


# In[198]:


hist = pd.DataFrame(history.history)
hist.to_csv('FinalReluLessSimple.csv')
hist['epoch'] = history.epoch
hist.tail()


# In[199]:


def plot_history(history):
  hist = pd.DataFrame(history.history)
  hist['epoch'] = history.epoch
  
  plt.figure()
  plt.xlabel('Epoch')
  plt.ylabel('Mean Abs Error [Price]')
  #plt.plot(hist['epoch'], hist['mean_absolute_error'],
   #        label='Train Error')
  plt.plot(hist['epoch'], hist['val_mean_absolute_error'],
           label = 'Val Error')
  plt.ylim([0,3000])
  plt.legend()
  

  plt.figure()
  plt.xlabel('Epoch')
  plt.ylabel('Mean Abs Error [Price]')
  plt.plot(hist['epoch'], hist['mean_absolute_error'],
           label='Train Error')
#  plt.plot(hist['epoch'], hist['val_mean_absolute_error'],
 #          label = 'Val Error')
  plt.ylim([0,2000])
  plt.legend()
  


  plt.figure()
  plt.xlabel('Epoch')
  plt.ylabel('Mean Square Error [$MPG^2$]')
  plt.plot(hist['epoch'], hist['mean_squared_error'],
           label='Train Error')
  plt.plot(hist['epoch'], hist['val_mean_squared_error'],
           label = 'Val Error')
  plt.ylim([0,1000000])
  plt.legend()
  plt.show()


plot_history(history)

