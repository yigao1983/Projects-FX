fx_pattern:{[date_beg;date_end;cur_pair;venue]
    
    trade_tab:select sym:first sym,trade_size:sum trade_size,dbname:first dbname 
     by date,3600000 xbar sun_time.time from
     .st.unenum select date,sun_time:.st.tz2gmt[.st.sys.db_timezones[.layer.db;`tz];sun_time],
     sym,trade_size:`long$trade_size,dbname from trades
     where date within (date_beg,date_end),sym=cur_pair,dbname=venue;
    
    pattern_tab:select sym:first sym,trade_size:avg trade_size,dbname:first dbname 
     by time from trade_tab;
    
    :pattern_tab;
 };
