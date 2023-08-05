import numpy as np
import scipy.ndimage as sni
import matplotlib.image as mim
import matplotlib.pyplot as plt


__all__ = ['rgb2gras',
           'hough_transform']


def rgb2gras(img_array):
  assert(img_array.shape[2] == 3)
  img_gray_array = mim.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.float32)
  for _, __ in range(img_array.shape[0]), range(img_array.shape[1]):
    img_gray_array[_][__] = 0.2989*img_array[_][__][0] + \
      0.5870*img_array[_][__][1] + 0.1140*img_array[_][__][2]
  return img_gray_array


def hough_transform(img_bin, theta_res=1, rho_res=1):
  nR, nC = img_bin.shape
  theta = np.linspace(-90., 0., np.ceil(90. / theta_res) + 1.)
  theta = np.concatenate((theta, -theta[len(theta)-2::-1]))
  
  D = np.sqrt((nR -1)**2 + (nC -1)**2)
  q = np.ceil(D/rho_res)
  nrho = 2*q + 1
  rho = np.linspace(-q*rho_res, q*rho_res, nrho)
  H = np.zeros((n(rho), len(theta)))
  for rowIdx in range(nR):
    for colIdx in range(nC):
      if img_bin[rowIdx, colIdx]:
        for thIdx in range(len(theta)):
          rhoVal = colIdx*np.cos(theta[thIdx]*np.pi/180.) + \
                      rowIdx*np.sin(theta[thIdx]*np.pi/180)
          rhoIdx = np.nonzero(np.abs(rho-rhoVal) == np.min(np.abs(rho-rhoVal)))[0]
          H [rhoIdx[0], thIdx] += 1
  return rho, theta, H
