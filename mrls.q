.utl.mrls:{[tbl;xCols;yCol;ff]

    x:tbl[xCols];
    y:tbl[yCol];

    id:{(x,x)#1f,x#0f}[count x];

    state:(`B`P)!(count[x]?0f;id);

    res:{[id;ff;stateN;xN;yN]
        P_0:stateN[`P];
        B_0:stateN[`B];

        L:mmu[P_0;xN]%((ff + mmu[xN;mmu[P_0;xN]]));

        P:mmu[(id - (flip enlist L) mmu  (enlist xN));P_0]%ff;
        B:B_0 + L*(yN - mmu[xN;B_0]);

        :(`B`P)!(B;P);
    }[id;ff]\[state;flip x;y];

    :res;

 };
