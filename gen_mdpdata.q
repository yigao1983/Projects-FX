.alpha.genMDPData:{[a]

    / Book Pre-Processor
    dd:(`sDate`eDate`sym`venue`fwdTicks)!(.z.d-28;.z.d-1;`AUDUSD;`HS_SUNTRADINGA_nv;1);
    dd:dd,a;

    / Get D2 data
    system "l /data/db_tdc_fx_books";
    bkData:.st.unenum `sun_time xasc select sun_time,spread1:0^ask_price1-bid_price1,ask_price1,bid_price1,obvi1:0^log[bid_size1%ask_size1],obvi2:0^log[bid_size[;1]%ask_size[;1]],lvlGap:0^log[(bid_price1-bid_price[;1])%(ask_price[;1]-ask_price1)] from book where date within (dd[`sDate],dd[`eDate]),sym=dd[`sym],dbname=dd[`venue],((deltas[ask_price1]<>0) or (deltas[bid_price1]<>0) or (deltas[ask_size1]<>0) or (deltas[bid_size1]<>0)),bid_price1<>0,ask_price1<>0,(ask_price1>=bid_price1);

    / Join Next D0 Mid
    bkData:aj[`sun_time;bkData;select sun_time,prev_mid:prev[(ask_price1+bid_price1)%2],target_mid:xprev[(neg dd[`fwdTicks]);(ask_price1+bid_price1)%2] from bkData where ((deltas[ask_price1]<>0) or (deltas[bid_price1]<>0))];
    bkData:select from bkData where prev_mid<>0n,target_mid<>0n;

    / Calculate Target Variable
    bkData:update target:0^log[target_mid%((ask_price1+bid_price1)%2)] from bkData;

    / Calculate AutoCorrelation Inputs
    bkData:update autoCorr1:0^log[((ask_price1+bid_price1)%2)%prev_mid] from bkData;
    bkData:update autoCorr2:0^prev[autoCorr1] from bkData;

    / Define update type
    :delete ask_price1,bid_price1,updateType,prev_mid,target_mid from update mid_price1:(ask_price1 + bid_price1)%2,updateType:deltas[((ask_price1+bid_price1)%2)]<>0 from bkData;

 };

.alpha.genMDP:{[a]

    dd:(`sDate`eDate`fwdTicks`venue`sym`coloID)!(.z.d-1;.z.d-1;10;`HS_SUNTRADINGB_nv;`AUDUSD;`NY4);
    dd:dd,a;

    / Get Data
    data:.alpha.genMDPData[dd];
    
    / Get Columns with values
    xCols:`;
    $[0=exec sum[obvi1<>0] from data;;xCols:xCols,`obvi1];
    $[0=exec sum[obvi2<>0] from data;;xCols:xCols,`obvi2];
    $[0=exec sum[lvlGap<>0] from data;;xCols:xCols,`lvlGap];
    $[0=exec sum[autoCorr1<>0] from data;;xCols:xCols,`autoCorr1];
    $[0=exec sum[autoCorr2<>0] from data;;xCols:xCols,`autoCorr2];
    xCols:xCols except `;

    / Cap Large X Variables
    data:update bookInvalid:0b from data;
    data:update bookInvalid:1b from data where (spread1 < 0) or (spread1 > {(asc x) floor .995*count x}[spread1]), mid_price1 = 0n;

    / Run Regression
    reg:.utl.multiLinReg[select from data where not bookInvalid;xCols;`target];

    / Gen MDP Mid
    data:update mdp_mid:mid_price1*exp[mmu[reg[`b];data[xCols]]] from data;

    / Filter
    publish_tolerance:exec 0.5e-5*med[mdp_mid] from data;
    data:update publishAlpha:{[thr;x;y] ?[abs[x+y]>thr;0f;x+y] }[publish_tolerance]\[0f;0^deltas mdp_mid] from data where not bookInvalid;
    data2:select sun_time, spread1, mid_price1, mdp_mid, bookInvalid from data where publishAlpha = 0f;

    / Save data to CSV
    /(`$":/mnt/sdauto/kdbshares/kx.silver/Andrew/Alpha/MDP/MDP_OUTPUT/",string[dd`coloID],"_",string[dd[`sym]],"_",string[dd[`venue]],".csv") 0: csv 0: data;

    / Save Weights to CSV
    weights:flip (`name`value)!(xCols,`max_spread`publish_tolerance;reg[`b],(exec max spread1 from data where not bookInvalid),publish_tolerance);
    (`$":/mnt/sdauto/kdbshares/kx.silver/Andrew/Alpha/MDP/MDP_OUTPUT/",string[dd`coloID],"_",string[dd[`sym]],"_",string[dd[`venue]],"_WEIGHTS.csv") 0: csv 0: weights;

 };
