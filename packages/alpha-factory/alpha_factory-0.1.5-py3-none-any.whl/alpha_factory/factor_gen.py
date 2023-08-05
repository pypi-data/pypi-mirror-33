# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:32:58 2018

@author: yili.peng
"""

from .cprint import cprint
from .check_mem import clean
from .generator_core import generate_batch #,generate_batch_mul
from RNWS import read
from glob import glob
import pandas as pd
import time
import warnings
warnings.simplefilter('ignore')


def find_dependency(df):
    return tuple(df.index[df['dependency'].isnull()])

def find_all_factors(path):
    pathlist=[[i,glob(i+'/factor_[0-9]*.csv')[1]] for i in glob(path+'/factor_part[0-9]*')]
    factor_list=[]
    for p in pathlist:
        line=open(p[1],'r').readline()
        factor_list.append([p[0],line.strip('\n').split(',')[1:]])
    return factor_list

def find_part(path):
    try:
        a=max([int(i[-3:]) for i in glob(path+'/*')])+1
    except:
        a=0
    return a

class generator_class:
    def __init__(self,df,factor_path,**parms):
        '''
        df: factor dataframe
        factor_path: root path to store factors
        **parms: all dependency dataframes
        '''
        flag=[i in parms.keys() for i in df.loc[df['dependency'].isnull(),'df_name']]
        if not all(flag):
            print('dependency:',find_dependency(df))
            raise Exception('need all dependencies')
        self.parms=parms
        self.df=df
        self.batch_num=find_part(factor_path)
        self.factor_path=factor_path
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    def reload_factors(self,**kwargs):
        factor_list=find_all_factors(self.factor_path)
        if len(factor_list)==0:
            pass
        else:
            for l in find_all_factors(self.factor_path):
                path=l[0]
                factors=l[1]
                print('reload: ',path)
                factor_exposures=read.read_df(path=path,file_pattern='factor',header=0,dat_col=factors,**kwargs)
                self.parms.update({factors[i]:factor_exposures[i] for i in range(len(factors))})
    def reload_df(self,path,**kwargs):
        self.df=pd.read_csv(filepath_or_buffer=path,**kwargs)
    def output_df(self,path,**kwargs):
        self.df.to_csv(path_or_buf=path,index=False,**kwargs)
    def generator(self,name_start='a',batch_size=50,):#multi=False,processors=None
        '''
        multiprocessing is deprecated due to vast memory sharing problem
        '''
        cprint('\nGenerating one batch start',c='',f='l')
        t0=time.time()
#        if multi:
#            new_df,new_parms=generate_batch_mul(self.df,batch_size=batch_size,out_file_path=self.factor_path+'/factor_part'+str(self.batch_num).zfill(3),name_start=name_start,processors=processors,**self.parms)
#        else:
        new_df,new_parms=generate_batch(self.df,batch_size=batch_size,out_file_path=self.factor_path+'/factor_part'+str(self.batch_num).zfill(3),name_start=name_start,**self.parms)
        self.parms.update(new_parms)
        self.df=new_df
        self.batch_num+=1
        t1=time.time()
        cprint('Generating one batch finished --- time %.3f s\n'%(t1-t0),c='',f='l')
        new_df=new_parms=t0=t1=None
        clean()
        