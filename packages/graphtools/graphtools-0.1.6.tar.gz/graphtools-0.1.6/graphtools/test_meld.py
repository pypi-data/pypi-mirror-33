import phate
import os
import time
import pandas as pd
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats.mstats import zscore
from scipy.stats import pearsonr
import sys
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import graphtools as gt
import pygsp
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize


def jitter(vec):
    sigma = .8 / len(set(vec))
    return np.random.normal(0, sigma, len(vec)) + vec

# Build Kernel & Visualize

# Get "technical batches" using spectral clustering

d = np.load(
    '/home/dan/data/burkhardt/zebrafish/schier_developmental_trajectories/10xMZoep6S/processed_data.npz')
data_ln = d['data_ln']
gene_names = d['gene_names']
samples = d['samples']
pca_clusters = d['pca_clusters']

batch = []
for pc, si in zip(pca_clusters, samples):
    if pc == 1:
        if si == 1:
            batch.append(0)
        else:
            batch.append(1)
    else:
        if si == 1:
            batch.append(2)
        else:
            batch.append(3)

batch = np.array(batch)


# MNN Kernel
# "matrix gamma"

bs = .99
br = 0.5  # 0   1   2    3
G = np.array([[1,  bs, br, bs],  # 0
              [bs,  1, bs, br],  # 1
              [br, bs,  1, bs],  # 2
              [bs, br, bs,  1]])  # 3"

# Build kernel, get fourier basis, compute embedding

tic = time.time()
g = gt.Graph(np.sqrt(data_ln), n_pca=100, knn=11, decay=50, use_pygsp=True,
             gamma=G, kernel_symm='gamma', sample_idx=batch, thresh=1e-6,
             random_state=42, verbose=2,
             adaptive_k='none')

pca = PCA(n_components=100, random_state=42).fit(np.sqrt(data_ln))
X = pca.transform(np.sqrt(data_ln))
k = 10
a = 50
sample_idx = batch
beta = 0
metric = 'euclidean'
gamma = G
from scipy.spatial.distance import cdist

one_sample = (sample_idx is None) or (
    np.sum(sample_idx) == len(sample_idx))
if not one_sample:
    if not (0 <= beta <= 1):
        raise ValueError('Beta must be in the half-open interval (0:1]')
else:
    sample_idx = np.ones(len(X))

samples = np.unique(sample_idx)

K = np.zeros((len(X), len(X)))
K[:] = np.nan
K = pd.DataFrame(K)

# Build KNN kernel
tic = time.time()
for si in samples:
    X_i = X[sample_idx == si]            # get observations in sample i
    for sj in samples:
        X_j = X[sample_idx == sj]        # get observation in sample j
        pdx_ij = cdist(X_i, X_j, metric=metric)  # pairwise distances
        kdx_ij = np.sort(pdx_ij, axis=1)  # get kNN
        e_ij = kdx_ij[:, k]             # dist to kNN
        pdxe_ij = pdx_ij / e_ij[:, np.newaxis]  # normalize
        k_ij = np.exp(-1 * (pdxe_ij ** a))  # apply α-decaying kernel
        if si == sj:
            if one_sample:
                # fill out values in K for NN on diagnoal
                K.iloc[sample_idx == si, sample_idx == sj] = k_ij
            else:
                K.iloc[sample_idx == si, sample_idx == sj] = k_ij * \
                    (1 - beta)  # fill out values in K for NN on diagnoal
        else:
            # fill out values in K for NN on diagnoal
            K.iloc[sample_idx == si, sample_idx == sj] = k_ij

if np.shape(gamma) == ():
    K = (gamma * np.minimum(K, K.T)) + \
        ((1 - gamma) * np.maximum(K, K.T))
else:
    # Gamma can be a matrix with specific values transitions for each batch
    # This allows for technical replicates and experimental samples to be
    # Corrected simulatenously
    if not np.shape(gamma)[0] == len(set(sample_idx)):
        raise ValueError(
            'Matrix gamma must have one entry per I -> J kernel')
    # Filling out gamma (n_samples, n_samples) to G (n_cells, n_cells)
    G = pd.DataFrame(np.zeros((len(sample_idx), len(sample_idx))))
    for ix, si in enumerate(set(sample_idx)):
        for jx, sj in enumerate(set(sample_idx)):
            G.iloc[sample_idx == si, sample_idx == sj] = gamma[ix, jx]
    K = (G * np.minimum(K, K.T)) + ((1 - G) * np.maximum(K, K.T))

diff_op = normalize(K, 'l1', axis=1)
