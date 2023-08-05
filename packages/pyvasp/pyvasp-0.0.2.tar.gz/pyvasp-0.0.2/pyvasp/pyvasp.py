#!/usr/bin/env python3
#DESCRIPTION: a multi-option python script for vasp data manupulation
#LICENSE: MIT
#AUTHOR: Wen-Bo Fu
#MAIL: fuwenbo17@gscaep.ac.cn
#VERSION: 0.0.2

#################### usage functions ####################
def force_plot(start_step):
    import subprocess as sp
    import numpy as np
    import matplotlib.pyplot as plt 

    sh_cmd = ("grep 'ions per type' OUTCAR | awk '{print $5+$6+$7+$8+$9+$10}'",
              "grep -A {} TOTAL-FORCE OUTCAR",
              "grep EDIFFG INCAR| awk '{print $3}'")
    
    atomNum = int(sp.run(sh_cmd[0], stdout=sp.PIPE ,shell=True).stdout)
    forceCriterion = -1*float(sp.run(sh_cmd[2], stdout=sp.PIPE ,shell=True).stdout)
    tmp1 = sp.run(sh_cmd[1].format(atomNum+1, atomNum), stdout=sp.PIPE ,shell=True).stdout.decode().splitlines()
    ionStep = int((len(tmp1)+1)/(atomNum+3))
    
    tmp2 = []
    for i in range(1, ionStep+1):
        tmp2[((i-1)*atomNum):(i*atomNum-1)] = tmp1[((i-1)*atomNum+i*3-1):(i*atomNum+i*3-1)]
    
    data = np.array([i.split() for i in tmp2]).astype(float)
    
    max_force = np.zeros((ionStep, 3))
    for j in range(ionStep):
        max_force[j, :] = np.max(np.abs(data[(j*atomNum):((j+1)*atomNum-1), 3:]), axis=0)
    
    step = [k+1 for k in range(ionStep)]
    list = ['x', 'y', 'z']
    for l in range(3):
        plt.plot(step[start_step:], max_force[start_step:, l], label=list[l])
    plt.xlim((np.min(step[start_step:]), np.max(step[start_step:])))
    plt.hlines(forceCriterion, np.min(step[start_step:]), np.max(step[start_step:]))
    plt.xlabel('step')
    plt.ylabel('max_force/eV*A-1')
    plt.legend()
    plt.show()

def md_plot(start_step):
    import subprocess as sp
    import numpy as np
    import matplotlib.pyplot as plt 

    sh_cmd = ("grep POTIM INCAR | awk '{print $3}'",
              "grep T= OSZICAR | awk '{printf(\"%f %f %f %f %f\\n\", $1, $11, $3, $7, $5)}'")

    timestep = float(sp.run(sh_cmd[0], stdout=sp.PIPE ,shell=True).stdout)
    tmp = sp.run(sh_cmd[1], stdout=sp.PIPE ,shell=True).stdout.decode()
    data = np.array([i.split() for i in tmp.splitlines()]).astype(float)
    data[:, 0] *= timestep

    plt_list = [data[start_step:, i+1] for i in range(4)]
    label_list = ['Kinetic Energy', 'Temperature', 'Potential Energy', 'Total Energy']
    unit_list = ['eV', 'T', 'eV', 'eV']
    for i in range(4):
        plt.subplot(2,2,i+1)
        plt.plot(data[start_step:, 0], plt_list[i], 'red', label=label_list[i])
        plt.xlim((np.min(data[start_step:, 0]), np.max(data[start_step:, 0])))
        plt.ylim((np.min(plt_list[i]), np.max(plt_list[i])))
        plt.xlabel('step/fs', {'fontsize':'large', 'verticalalignment':'center', 'horizontalalignment':'center'})
        plt.ylabel(label_list[i]+'/'+unit_list[i], {'fontsize':'large', 'verticalalignment':'center', 'horizontalalignment':'center'})
        plt.title(label_list[i], {'fontsize':'xx-large', 'fontweight':'medium'}, color='g')
    plt.tight_layout() 
    plt.show()

def barr_get(image_num):
    import subprocess as sp
    import numpy as np

    sh_cmd = ("for i in `seq 0 1 {}`; do grep TOTEN 0$i/OUTCAR | tail -1 | awk -v i=$i '{{printf(\"%f %f\\n\", i, $5)}}'; done",)
    tmp = sp.run(sh_cmd[0].format(image_num+1), stdout=sp.PIPE ,shell=True).stdout.decode()
    data = np.array([i.split() for i in tmp.splitlines()]).astype(float)
    np.savetxt('barr', data)

def barr_plot():
    import matplotlib.pyplot as plt 
    import numpy as np
    from scipy.interpolate import interp1d

    data = np.loadtxt('barr')
    ix = data[:, 0]
    iy = data[:, 1] - data[0, 1]
    tx = np.linspace(ix.min(), ix.max(), 300)
    ty = interp1d(ix, iy, kind='cubic')(tx)
    plt.plot(tx, ty, color='red')
    plt.scatter(ix, iy)
    plt.show()

#################### main function ####################
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='pv', prefix_chars='-',
        description='Multi-option python program for visualization of VASP data')

    parser.add_argument(
        '-f', dest='fp', metavar='N',
        nargs='?', const=0, default=None, type=int,
        help='plot max-force vs ion-step from Nth (default: %(const)s) step')
    parser.add_argument(
        '-g', dest='bg', metavar='N',
        nargs='?', const=5, default=None, type=int,
        help='get energy barrier file of N (default: %(const)s) images')
    parser.add_argument(
        '-m', dest='mp', metavar='N',
        nargs='?', const=0, default=None, type=int,
        help='plot Ek, Ep, T, Etot of md from Nth (default: %(const)s) fs')
    parser.add_argument(
        '-p', dest='bp', action='store_true',
        help='plot barrier energy vs images from barrier file')

    args = parser.parse_args()
    if args.fp != None:
        force_plot(args.fp)
    if args.bg != None:
        barr_get(args.bg)
    if args.mp != None:
        md_plot(args.mp)
    if args.bp:
        barr_plot()
