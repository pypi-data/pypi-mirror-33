# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 15:33:46 2018

@author: yili.peng
"""
from .cprint import cprint,wrap_text
import pandas as pd
import numpy as np

def not_na(df,na_thresh=0.6,**kwarg):
    '''
    df: current generated df
    na_thresh: \u2208(0,1). Threshold of na portion. 
    '''
    if np.prod(df.shape)==0:
        cprint('\u2191\u2191\u2191'+wrap_text('is na')+'\u2191\u2191\u2191')
        return False
    na_pct=df.isna().sum().sum()/np.prod(df.shape)
    if na_pct>na_thresh:
        cprint('\u2191\u2191\u2191'+wrap_text('is na')+'\u2191\u2191\u2191')
        return False
    return True

def not_same(df,**kwarg):
    '''
    df: current generated df
    '''
    if df.max().max()==df.min().min():
        cprint('\u2191\u2191\u2191'+wrap_text('is same')+'\u2191\u2191\u2191')
        return False
    return True

def not_duplicated(df,old_df_dict,cor_thresh=0.7,**kwarg):
    '''
    df: current generated df
    old_df_dict: past generated df dictionary
    cor_thresh: \u2208(0,1). Threshold to start random choice. Probability = (1-cor)I(cor>cor_thresh)/(1-cor_thresh) 
    '''
    for key,old_df in old_df_dict.items():
        cor=pd.concat([df,old_df],keys=['new','old']).unstack().dropna(axis=1).T.corr().iloc[0,1]
        if abs(cor) > cor_thresh:
            cprint('\u2191\u2191\u2191'+wrap_text('is cor %s %.2f'%(key,cor))+'\u2191\u2191\u2191')
            prob=abs((1-abs(cor))/(1-cor_thresh))
            if np.random.choice([True,False],p=[prob,1-prob]):
                pass
            else:
                return False
    return True

def is_validate(df,old_df_dict,**kwarg):
    if not not_na(df,**kwarg):
        return False
    elif not not_same(df,**kwarg):
        return False
    elif not not_duplicated(df,old_df_dict,**kwarg):
        return False
    else:
        return True