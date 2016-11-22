import numpy as np
import pandas as pd
import qpython.qconnection as qconn
#import matplotlib.pyplot as plt
#import smtplib
#import email.mime.multipart as multipart
#import email.mime.text as text

class MDPAnalytics(object):
    
    def __init__(self, date_beg, date_end, sym, fwd_ticks, **kwargs):
        
        self.__date_beg = date_beg
        self.__date_end = date_end
        self.__sym = sym
        self.__fwd_ticks = fwd_ticks
        
        self.__hostname = kwargs["hostname"]
        self.__portnum  = kwargs["portnum"]
        self.__username = kwargs["username"]
        self.__password = kwargs["password"]
        
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
    
    def get_mdp_df(self):
        
        with open('gen_mdpdata.q', 'r') as fp:
            read_mdpdata = fp.read()
        with open('mrls.q', 'r') as fp:
            mrls_function = fp.read()
        
        try:
            self.__q.sync(read_mdpdata)
            self.__q.sync(mrls_function)
            self.__q.sync('cont:`sDate`eDate`sym`fwdTicks!({};{};`{};{})'.
                          format(self.__date_beg, self.__date_end, self.__sym, self.__fwd_ticks))
            self.__q.sync('mdp_tab:.alpha.genMDPData(cont);')
            #self.__q.sync('result:.utl.mrls[mdp_tab;`spread1`obvi1;`target;1.0];')
            #result = self.__q.sync('result')
            #print(result)
            
            self.__mdp_df = self.__q.sync('mdp_tab', pandas=True)
        
        except Exception as e:
            print(e)
        
        return self
    
    def output_mdp_df(self):
        
        try:
            self.__mdp_df.to_csv('mdp_{}_{}_{}.csv'.format(self.__sym, self.__date_beg, self.__date_end))
        except Exception as e:
            print(e)
        
        return self
    
if __name__ == "__main__":
    
    kwargs = {"hostname": "kdb1", "portnum": 10101, "username": "ygao", "password": "Password23"}
    
    date_beg = "2016.11.15"
    date_end = "2016.11.15"
    sym = "AUDUSD"
    fwd_ticks = 1
    
    mdp = MDPAnalytics(date_beg, date_end, sym, fwd_ticks, **kwargs).get_mdp_df().output_mdp_df()
