.utl.rls:{[tbl;xCol;yCol;ff]
    x:tbl[xCol];
    y:tbl[yCol];
    state:(`B`P)!(0f;var[x]);
    res:{[ff;stateN;xN;yN]
        P_0:stateN[`P];
        B_0:stateN[`B];
        L:P_0*xN*(1%(ff + xN*P_0*xN));
        P:((1 - L*xN)*P_0)%ff;
        B:B_0 + L*(yN - xN*B_0);
        :(`B`P)!(B;P);
    }[ff]\[state;x;y];
    :res[`B];
 }
