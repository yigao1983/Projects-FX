import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import FXActivity

def combine_df(date_beg, date_end, act_df_lst):
    
    for df in act_df_lst:
        sym = set(df.sym).pop()
        dbname = set(df.dbname).pop()
        df.drop(["sym", "dbname"], axis=1, inplace=True)
        df.columns = [dbname]
        df[dbname] = df[dbname] / df[dbname].sum()
        
    cur_pair_df = pd.concat(act_df_lst, axis=1)
    
    
    style_lst = ['-', '--', ':'] * 4
    
    ax = cur_pair_df.plot(x=pd.to_datetime(cur_pair_df.index.values), style=style_lst, colormap="rainbow", linewidth=2)
    ax.legend(frameon=False, fontsize=10)
    ax.set_xticklabels(pd.to_datetime(cur_pair_df.index.values).strftime("%H:%M"))
    ax.set_xlabel("Time (GMT)", fontsize=14)
    ax.set_ylabel("Normalized trade size", fontsize=14)
    ax.set_title("{} ({} to {})".format(sym, date_beg, date_end))
    plt.savefig("pattern_{}_{}_{}.pdf".format(sym, date_beg, date_end), bbox_inches="tight")
    
    cur_pair_df = cur_pair_df[(cur_pair_df > 0.025).all(axis=1)]
    cur_pair_df.to_csv("pattern_{}_{}_{}.csv".format(sym, date_beg, date_end))
    
def main():
    
    kwargs = {"hostname": "kdb2", "portnum": 10102, "username": "ygao", "password": "Password23", \
              "database": "/data/db_tdc_fx_books", "trades": "trades"}
    
    date_beg = "2016.09.04"
    date_end = "2016.11.30"
    
    fx_pairs = ['EURUSD', 'EURUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'EURNOK', 'EURSEK', 'USDMXN', 'USDZAR']
    venue_lst = ['CNX_nv', 'HS_SUNTRADINGA_nv', 'HS_SUNTRADINGB_nv', 'BARCFX2_nv', 'JPMFX2_nv', 'CITADEL_nv', 'GAINGTX_nv']
    
    for sym in fx_pairs:
        act_df_lst = []
        for venue in venue_lst:
            act = FXActivity.FXActivity(date_beg, date_end, sym, venue, **kwargs).get_act_df()#.output_act_df()
            if not act.act_df.empty:
                act_df_lst.append(act.act_df)
        combine_df(date_beg, date_end, act_df_lst)
        
if __name__ == "__main__":
    
    main()
