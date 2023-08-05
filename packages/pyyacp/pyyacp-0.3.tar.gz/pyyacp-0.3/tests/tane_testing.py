from profiler.fdprofiler import TANEAlgorithm

tane= TANEAlgorithm()
size=10000
colNo=20
def f(i,k):
    if k==2:
        return 2
    else:
        return i*k
cols={k:[f(i,k) for i in range(0,size)] for k in range(1,colNo+1)}
import time
s=time.time()
print tane.analyse_cols(cols.values())
print (time.time()-s)*1000