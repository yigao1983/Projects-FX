.utl.mrls:{[tbl;xCols;yCol;ff]
    
    / x:tbl[xCols];
    / y:tbl[yCol];
    
    x:each [{x % dev x}] tbl[xCols];
    y:tbl[yCol];
    
    id:{(x,x)#1f,x#0f}[count x];
    
    state:(`B`P`R)!(count[x]?0f;id;0f);
    
    res:{[id;ff;stateN;xN;yN]
        P_0:stateN[`P];
        B_0:stateN[`B];
        
        R:yN - mmu[xN;B_0];
        
        L:mmu[P_0;xN]%((ff + mmu[xN;mmu[P_0;xN]]));
        
        P:mmu[(id - (flip enlist L) mmu  (enlist xN));P_0]%ff;
        B:B_0 + L*R;
        
        :(`B`P`R)!(B;P;R);
    }[id;ff]\[state;flip x;y];
    
    :res[`R];
    
 };
