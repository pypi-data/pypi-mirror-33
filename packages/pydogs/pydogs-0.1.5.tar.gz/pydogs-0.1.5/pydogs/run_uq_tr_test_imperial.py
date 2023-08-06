import numpy as np
import dogs, uq
import scipy.io as io
import tr

# The second time of running the algorithm.
yE = np.array([])
SigmaT = np.array([])
T = np.array([])
IND = np.array([])

# Read from surr_J_new.
var = io.loadmat("data/params.mat")
A = var['A']
theta = var['theta']



fname = "data/dragdata0"+str(1)+".dat"
zs = np.loadtxt(fname)


for ii in range(1,12):
    print(ii)
    # go to datadrag files
    pname = os.listdir('./data')
    fname = './data/'+ pname[ii]
    zs = np.loadtxt(fname)



    trans_samples = int(np.ceil(len(zs)*0.005))
    print(trans_samples)
    xx = uq.data_moving_average(zs, trans_samples).values
    ind = tr.transient_removal(xx)

    # sig = np.sqrt(uq.stationary_statistical_learning_reduced(xx[ind:], 18)[0])
    t = len(zs)  # not needed for Alpha-DOGS
    T = np.hstack((T, t))  # not needed for Alpha-DOGS
    print("-------------------")
    print(' len of transient = ',int(ind/len(xx)*T[ii-1]) )
    print(' total  len is: ', T[ii-1])
    J = np.abs(np.mean(xx[ind:]))

    yE = np.hstack((yE, J))
    # SigmaT = np.hstack((SigmaT, sig))

    IND = np.hstack((IND, int(ind/len(xx)*T[ii-1])))

    # data = {'yE': yE, 'SigmaT': SigmaT, 'T': T}
    # io.savemat("allpoints/Yall", data)

    print("The second time running the iteration")
    print(' len of yE = ', len(yE))
    # print('iter k = ', k)
    print('function evaluation at this iteration: ', J)
    # print(' time averaging error at this iteration: ', sig)
