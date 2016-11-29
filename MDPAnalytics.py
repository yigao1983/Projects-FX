import os
import numpy as np
import pandas as pd
import qpython.qconnection as qconn
import matplotlib.pyplot as plt
import RLS

class MDPAnalytics(object):
    
    def __init__(self, date_beg, date_end, sym, venue, fwd_ticks, **kwargs):
        
        self.__date_beg = date_beg
        self.__date_end = date_end
        self.__sym = sym
        self.__venue = venue
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
    
    @property
    def mdp_df(self):
        
        return self.__mdp_df
    
    def get_mdp_df(self):
        
        self.__mdp_csv = 'mdp_{}_{}_{}_{}.csv'.format(self.__sym, self.__venue, self.__date_beg, self.__date_end)
        
        if os.path.isfile(self.__mdp_csv):
            
            self.__mdp_df = pd.read_csv(self.__mdp_csv)
            self.__mdp_df.set_index('sun_time', drop=True, inplace=True)
            self.__mdp_df.index = pd.to_datetime(self.__mdp_df.index)
            
            try:
                self.__q('set', 'mdp_tab', self.__mdp_df)
            except Exception as e:
                print(e)
            
        else:
            
            with open('gen_mdpdata.q', 'r') as fp:
                read_mdpdata = fp.read()
            
            try:
                self.__q.sync(read_mdpdata)
                self.__q.sync('cont:`sDate`eDate`sym`venue`fwdTicks!({};{};`{};`{};{})'.
                              format(self.__date_beg, self.__date_end, self.__sym, self.__venue, self.__fwd_ticks))
                self.__q.sync('mdp_tab:.alpha.genMDPData(cont);')
                self.__q.sync('mdp_tab:.st.unenum select from mdp_tab where abs[target]<5*med[abs[target]];')
                self.__q.sync('mdp_tab:.st.unenum select from mdp_tab where all not null flip mdp_tab;')
                
                self.__mdp_df = self.__q.sync('mdp_tab', pandas=True)
                self.__mdp_df.set_index('sun_time', drop=True, inplace=True)
                self.__mdp_df.index = pd.to_datetime(self.__mdp_df.index)
                
                self.output_mdp_df()
                
            except Exception as e:
                print(e)
        
        return self
    
    def output_mdp_df(self):
        
        try:
            self.__mdp_df.to_csv(self.__mdp_csv)
        except Exception as e:
            print(e)
        
        return self
     
    def mrls_regression(self, ff=1.0):
        
        with open('mrls.q', 'r') as fp:
            mrls_function = fp.read()
            
        try:
            self.__q.sync(mrls_function)
            self.__q.sync('resid_lst:.utl.mrls[mdp_tab;`spread1`obvi1`obvi2`lvlGap`autoCorr1`autoCorr2`mid_price1;`target;{}]'.
                          format(ff))
            self.__resid_q = np.array(self.__q.sync('resid_lst'))
            
            r2 = 1.0 - np.var(self.__resid_q, ddof=0) / np.var(self.__mdp_df.target.values, ddof=0)
            
        except Exception as e:
            print(e)
        
        return r2
    
    def get_mrls_df(self):
        
        ff_rng = [0.9, 0.925, 0.95, 0.975, 0.99, 0.999, 0.9999, 0.99999, 0.999999, 1.0]
        
        r2_lst = [self.mrls_regression(ff) for ff in ff_rng]
        
        self.__mrls_df = pd.DataFrame({'ff': ff_rng, 'r2': r2_lst}).set_index('ff', drop=True)
        
        self.output_mrls_df()
        
        return self
    
    def output_mrls_df(self):
        
        self.__mrls_df.to_csv('mrls_{}_{}_{}_{}.csv'.format(self.__sym, self.__venue, self.__date_beg, self.__date_end))
        
        return self
    
if __name__ == "__main__":
    
    kwargs = {"hostname": "kdb1", "portnum": 10101, "username": "ygao", "password": "Password23"}
    
    date_beg = "2016.11.15"
    date_end = "2016.11.15"
    sym = "AUDUSD"
    venue = "HS_SUNTRADINGA_nv"
    fwd_ticks = 1
    
    mdp = MDPAnalytics(date_beg, date_end, sym, venue, fwd_ticks, **kwargs).get_mdp_df().get_mrls_df()
