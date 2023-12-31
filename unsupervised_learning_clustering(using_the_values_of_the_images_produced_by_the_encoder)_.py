# -*- coding: utf-8 -*-
"""Unsupervised_learning_Clustering(using the values of the images produced by the encoder) .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K0lRy7qE77w___AEdqm3xrpEte0AlY6j
"""

# Import the necessary libraries
import numpy as np
from sklearn import cluster, datasets, metrics
import matplotlib.pyplot as plt
from sklearn import metrics

from sklearn.model_selection import train_test_split
from tensorflow.keras.datasets import fashion_mnist

import pandas as pd
import tensorflow as tf

from sklearn.metrics import accuracy_score, precision_score, recall_score
from tensorflow.keras import layers, losses

from tensorflow.keras.models import Model

#Define a performance evaluation function
def performance_score(input_values, cluster_indexes):
    try:
        silh_score = metrics.silhouette_score(input_values.reshape(-1, 1), cluster_indexes)
        print(' .. Silhouette Coefficient score is {:.2f}'.format(silh_score))
        #print( ' ... -1: incorrect, 0: overlapping, +1: highly dense clusts.')
    except:
        print(' .. Warning: could not calculate Silhouette Coefficient score.')
        silh_score = -999
    try:
        v_measure_score= metrics.v_measure_score(input_values, cluster_indexes)
        print(' .. V-measure   score is {:.2f}'.format(v_measure_score))
    except:
        print(' .. Warning: could not calculate V-measure   score.')
        v_measure_score = -999

    try:
        ch_score =\
         metrics.calinski_harabasz_score(input_values.reshape(-1, 1), cluster_indexes)
        print(' .. Calinski-Harabasz Index score is {:.2f}'.format(ch_score))
        #print(' ... Higher the value better the clusters.')
    except:
        print(' .. Warning: could not calculate Calinski-Harabasz Index score.')
        ch_score = -999

    try:
        db_score = metrics.davies_bouldin_score(input_values.reshape(-1, 1), cluster_indexes)
        print(' .. Davies-Bouldin Index score is {:.2f}'.format(db_score))
        #print(' ... 0: Lowest possible value, good partitioning.')
    except:
        print(' .. Warning: could not calculate Davies-Bouldin Index score.')
        db_score = -999

    return silh_score,mi, ch_score, db_score

#Import tha dataset
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
# normalize pixel values between 0 and 1
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = np.reshape(x_train, (len(x_train), 28, 28, 1)) 
x_test = np.reshape(x_test, (len(x_test), 28, 28, 1))
print(x_train.shape)
print(x_test.shape)

#split train to train the validate set
x_train, x_validate, y_train, y_validate =\
 train_test_split(x_train, y_train, test_size=0.1, random_state=1)

#set up a cnn autoencoder
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv2D, MaxPool2D,\
 UpSampling2D, Activation
# Build the autoencoder
model = Sequential()
model.add(Conv2D(14, kernel_size=3, padding='same',\
                 activation='relu', input_shape=(28,28,1)))
model.add(MaxPool2D((2,2), padding='same'))
model.add(Dropout(0.2))
model.add(Conv2D(7, kernel_size=3, padding='same', activation='relu'))
model.add(MaxPool2D((2,2), padding='same'))
model.add(Dropout(0.2))
model.add(Conv2D(7, kernel_size=3, padding='same', activation='relu'))
model.add(UpSampling2D((2,2)))
model.add(Dropout(0.2))
model.add(Conv2D(14, kernel_size=3, padding='same', activation='relu'))
model.add(UpSampling2D((2,2)))
model.add(Dropout(0.2))
model.add(Conv2D(1, kernel_size=3, padding='same', activation='relu'))

model.compile(optimizer='adam', loss="mse")
model.summary()

#train the model
model.fit(x_train, x_train, epochs=10, batch_size=64,\
          validation_data=(x_validate, x_validate), verbose=1)

# do some plotting for the reconstructed images
import matplotlib.pyplot as plt
restored_testing_dataset = model.predict(x_test)
# Observe the reconstructed image quality
fig2= plt.figure(figsize=(20,5))
for i in range(10):
    index = y_test.tolist().index(i)
    plt.subplot(2, 10, i+1)
    plt.imshow(x_test[index].reshape((28,28)))
    plt.gray()
    plt.subplot(2, 10, i+11)
    plt.imshow(restored_testing_dataset[index].reshape((28,28)))
    plt.gray()
fig2.savefig('restored.png')

#exctract the encoder block
from keras import backend as K
encoder = K.function([model.layers[0].input],[model.layers[4].output])

#convert images to projected data
test_encoded_images = encoder([x_test])[0].reshape(-1,7*7*7)

#use projections to cluster the images
from sklearn import cluster
for numOfClust in range (3,12):
    print('Currently testing', str(numOfClust),\
        'number of clusters')
    mbkm = cluster.MiniBatchKMeans(n_clusters = numOfClust)
    mbkm.fit(test_encoded_images)
    clusterLabels = mbkm.labels_
    # silh_score = metrics.silhouette_score(outputData.reshape(-1, 1), clusterLabels)
    silh_score, v_measure_score,  ch_score, db_score = \
    performance_score(y_test, clusterLabels)

#use minibatch kmeans with 10 clusters
# Cluster the training set
mbkm = cluster.MiniBatchKMeans(n_clusters = 10)
mbkm.fit(test_encoded_images)
clusterLabels = mbkm.labels_

#performance scores & visualizations
fig = plt.figure(figsize=(20,20))
for clusterIdx in range(10):
    # cluster = cm[r].argmax()
    for c, val in enumerate(x_test[clusterLabels == clusterIdx][0:10]):
        fig.add_subplot(10, 10, 10*clusterIdx+c+1)
        plt.imshow(val.reshape((28,28)))
        plt.gray()
        plt.xticks([])
        plt.yticks([])
        plt.xlabel('cluster: '+str(cluster))
        plt.ylabel('cluster: '+str(clusterIdx))

#Spectral clustering
#use projections to cluster the images
from sklearn.cluster import SpectralClustering
from sklearn import cluster
for numOfClust in range (3,12):
    print('Currently testing', str(numOfClust),\
        'number of clusters')
    sc = SpectralClustering(n_clusters = numOfClust,assign_labels='discretize',random_state=0)
    sc.fit(test_encoded_images)
    clusterLabels = sc.labels_
    
    silh_score,v_measure_score, ch_score, db_score = \
    performance_score(y_test, clusterLabels)

#use  Spectral Clustering with 10 clusters
# Cluster the training set
sc = SpectralClustering(n_clusters = 10,assign_labels='discretize',random_state=0)
sc.fit(test_encoded_images)
clusterLabels = sc.labels_

#performance scores & visualizations
fig = plt.figure(figsize=(20,20))
for clusterIdx in range(10):
    # cluster = cm[r].argmax()
    for c, val in enumerate(x_test[clusterLabels == clusterIdx][0:10]):
        fig.add_subplot(10, 10, 10*clusterIdx+c+1)
        plt.imshow(val.reshape((28,28)))
        plt.gray()
        plt.xticks([])
        plt.yticks([])
        plt.xlabel('cluster: '+str(cluster))
        plt.ylabel('cluster: '+str(clusterIdx))

#AgglomerativeClustering
#use projections to cluster the images
from sklearn.cluster import AgglomerativeClustering
from sklearn import cluster
for numOfClust in range (3,12):
    print('Currently testing', str(numOfClust),\
        'number of clusters')
    ac = AgglomerativeClustering(n_clusters = numOfClust)
    ac.fit(test_encoded_images)
    clusterLabels = ac.labels_
    
    silh_score,v_measure_score, ch_score, db_score = \
    performance_score(y_test, clusterLabels)

#use  AgglomerativeClusteringwith 10 clusters
# Cluster the training set
ac = AgglomerativeClustering(n_clusters = 10)
ac.fit(test_encoded_images)
clusterLabels = ac.labels_

#performance scores & visualizations
fig = plt.figure(figsize=(20,20))
for clusterIdx in range(10):
    # cluster = cm[r].argmax()
    for c, val in enumerate(x_test[clusterLabels == clusterIdx][0:10]):
        fig.add_subplot(10, 10, 10*clusterIdx+c+1)
        plt.imshow(val.reshape((28,28)))
        plt.gray()
        plt.xticks([])
        plt.yticks([])
        plt.xlabel('cluster: '+str(cluster))
        plt.ylabel('cluster: '+str(clusterIdx))

