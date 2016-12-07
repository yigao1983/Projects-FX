import os
import numpy as np
import pandas as pd
import qpython.qconnection as qconn
import matplotlib.pyplot as plt

class FXActivity(object):
    
    def __init__(self, date_beg, date_end, sym, venue, **kwargs):
        
        self.__date_beg = date_beg
        self.__date_end = date_end
        self.__sym = sym
        self.__venue = venue
        
        self.__hostname = kwargs["hostname"]
        self.__portnum  = kwargs["portnum"]
        self.__username = kwargs["username"]
        self.__password = kwargs["password"]
        self.__database = kwargs["database"]
        self.__trades   = kwargs["trades"]
        
        self.__q = qconn.QConnection(host=self.__hostname, port=self.__portnum, \
                                     username=self.__username, password=self.__password, \
                                     numpy_temporals=True)
        
        self.connect()
        
    def __del__(self):
        
        self.disconnect()
    
    def connect(self):
        
        try:
            self.__q.open()
        except Exception as e:
            print(e)
        
        return self
    
    def disconnect(self):
        
        if self.__q.is_connected():
            self.__q.close()
    
    @property
    def act_df(self):
        
        return self.__act_df
        
    def get_act_df(self):
        
        try:
            self.__q.sync('\l {}'.format(self.__database))
            self.__q.sync('date_beg:{};'.format(self.__date_beg))
            self.__q.sync('date_end:{};'.format(self.__date_end))
            self.__q.sync('cur_pair:`{};'.format(self.__sym))
            self.__q.sync('venue:`{};'.format(self.__venue))
            
            with open('fx_pattern.q', 'r') as fp:
                read_pattern = fp.read()
            
            self.__q.sync(read_pattern)
            self.__q.sync('pattern_tab:fx_pattern[date_beg;date_end;cur_pair;venue];')
            
            self.__act_df = self.__q.sync('pattern_tab', pandas=True)
            
        except Exception as e:
            print(e)
        
        return self
        
    def output_act_df(self):
        
        self.__act_df.to_csv("pattern_{}_{}_{}_{}.csv".format(self.__sym, self.__venue, self.__date_beg, self.__date_end))
        
        return self
    
if __name__ == "__main__":
    
    kwargs = {"hostname": "kdb2", "portnum": 10102, "username": "ygao", "password": "Password23", \
              "database": "/data/db_tdc_fx_books", "trades": "trades"}
    
    date_beg = "2016.09.04"
    date_end = "2016.11.30"
    
    fx_pairs = ['EURUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'EURNOK', 'EURSEK', 'USDMXN', 'USDZAR']
    venue_lst = ['CNX_nv', 'HS_SUNTRADINGA_nv', 'HS_SUNTRADINGB_nv', 'BARCFX2_nv', 'JPMFX2_nv', 'CITADEL_nv', 'GAINGTX_nv']
    
    for venue in venue_lst:
        for sym in fx_pairs:
            act = FXActivity(date_beg, date_end, sym, venue, **kwargs).get_act_df()#.output_act_df()
    
