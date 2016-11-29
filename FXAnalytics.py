import pandas as pd
import matplotlib.pyplot as plt
import MDPAnalytics as MDP

def main():
    
    kwargs = {"hostname": "kdb1", "portnum": 10101, "username": "ygao", "password": "Password23"}
    
    fwd_ticks = 1
    
    fx_pairs = ['EURUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'EURNOK', 'EURSEK', 'USDMXN', 'USDZAR']
    venue_lst = ['HS_SUNTRADINGA_nv', 'HS_SUNTRADINGB_nv', 'BARCFX2_nv', 'JPMFX2_nv', 'CITADEL_nv', 'GAINGTX_nv']
    
    date_rng = pd.date_range('2016-09-04', pd.to_datetime('today'), freq='W')
    ff_rng = [0.95, 0.975, 0.99, 0.999, 0.9999, 0.99999, 0.999999, 1.0]
    
    for sym in fx_pairs:
        for venue in venue_lst:
            
            mrls_df = pd.DataFrame(index=ff_rng)
            mrls_df.index.name = 'ff'
            
            for date in date_rng[:-1]:
                
                date_beg = date.strftime('%Y.%m.%d')
                date_end = (date + pd.Timedelta(days=6)).strftime('%Y.%m.%d')
                
                mdp = MDP.MDPAnalytics(date_beg, date_end, sym, venue, fwd_ticks, **kwargs).get_mdp_df().get_mrls_df(ff_rng)
                
                mrls_df['r2_{}_{}'.format(date_beg, date_end)] = mdp.mrls_df.r2
            
            mrls_df['Mean'] = mrls_df.mean(axis=1)
            mrls_df['Stderr'] = mrls_df.std(axis=1, ddof=0)
            mrls_df.to_csv('mrls_{}_{}.csv'.format(sym, venue))
            
            mrls_df.plot(y='Mean', fontsize=16, \
                         title='$R^2$ ({} {} {} to {})'.
                         format(sym, venue, date_rng[0].strftime('%Y.%m.%d'), date_rng[-1].strftime('%Y.%m.%d')))
            plt.savefig('mrls_{}_{}.pdf'.format(sym, venue))
    
if __name__ == "__main__":
    
    main()
    
