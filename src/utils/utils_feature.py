import numpy as np
import  math
from scipy.interpolate import interp1d
import scipy.linalg as LA
import numpy as np 
from skimage.transform import resize
from multiprocessing import Process
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import mne
import torch
import time


def compute_spectrum(org_sig, ps_SampleRate = 2000, ps_FreqSeg = 512, ps_MinFreqHz = 10, ps_MaxFreqHz = 500):
    def create_extended_sig(sig):
        s_len = len(sig)
        s_halflen = int(np.ceil(s_len/2)) + 1
        start_win = sig[:s_halflen] - sig[0]
        end_win = sig[s_len - s_halflen - 1:] - sig[-1]
        start_win = -start_win[::-1] + sig[0]
        end_win = -end_win[::-1] + sig[-1]
        final_sig = np.concatenate((start_win[:-1],sig, end_win[1:]))
        if len(final_sig)%2 == 0:
            final_sig = final_sig[:-1]
        return final_sig
    extend_sig = create_extended_sig(org_sig)
    extend_sig = torch.from_numpy(extend_sig)
    ps_StDevCycles = 3
    
    s_Len = len(extend_sig)
    s_HalfLen = math.floor(s_Len/2)+1
    v_WAxis = torch.linspace(0, 2*np.pi, s_Len)[:-1]* ps_SampleRate
    v_WAxisHalf = v_WAxis[:s_HalfLen].repeat(ps_FreqSeg, 1)
    v_FreqAxis = torch.linspace(ps_MaxFreqHz, ps_MinFreqHz,steps=ps_FreqSeg)
    v_WinFFT = torch.zeros(ps_FreqSeg, s_Len)
    s_StDevSec = (1 / v_FreqAxis) * ps_StDevCycles
    v_WinFFT[:, :s_HalfLen] = torch.exp(-0.5*torch.pow(v_WAxisHalf - (2 * torch.pi * v_FreqAxis.view(-1, 1)), 2) * (s_StDevSec**2).view(-1, 1))
    v_WinFFT = v_WinFFT * np.sqrt(s_Len)/ torch.norm(v_WinFFT, dim = -1).view(-1, 1)
    v_InputSignalFFT = torch.fft.fft(extend_sig)
    res = torch.fft.ifft(v_InputSignalFFT.view(1,-1)* v_WinFFT)/torch.sqrt(s_StDevSec).view(-1,1)
    ii, jj = int(len(org_sig)//2), int(len(org_sig)//2 + len(org_sig))
    res = np.abs(res[:, ii:jj].numpy())
    return res