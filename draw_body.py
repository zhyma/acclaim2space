import numpy as np
import matplotlib.pyplot as pl
from mpl_toolkits.mplot3d import Axes3D

class draw_body:
    fig = None
    ax = None
    joints = []
    '''
    input object array: [[float(x),float(y),float(z),int(parent)],...]
    '''
    def __init__(self, data_in):
        self.fig = pl.figure()
        self.ax = Axes3D(self.fig)
        
        self.joints = data_in
        

    '''
    draw all joints on the plot
    '''
    def draw_joints(self):
        for i in range(len(self.joints)):
            a = self.joints[i]
            self.ax.scatter(a[0],a[1],a[2],color='r')
            #print tags for joints
            self.ax.text(a[0],a[1],a[2],str(i),(1,1,0))
    
    '''
    draw all limbs on the plot
    '''
    def draw_limbs(self):
        for i in range(1,len(self.joints)):
            a = self.joints[i]
            start = [a[0],a[1],a[2]]
            b = self.joints[self.joints[i][3]]
            end = [b[0],b[1],b[2]]
            self.ax.plot([start[0],end[0]],[start[1],end[1]],[start[2],end[2]],'--',color='k')
    
    def draw(self):
        self.ax.clear()
        
        self.ax.plot([0,5],[0,0],[0,0],color='r')
        self.ax.plot([0,0],[0,5],[0,0],color='g')
        self.ax.plot([0,0],[0,0],[0,5],color='b')
        
        self.ax.view_init(elev=110, azim=-90)
        
        lim_max = abs(np.amax(self.joints[:,:3]))
        lim_min = abs(np.amin(self.joints[:,:3]))
        if lim_max > lim_min:
            end = lim_max
        else:
            end = lim_min
        self.ax.set_xlim3d(-end,end)
        self.ax.set_ylim3d(-end,end)
        self.ax.set_zlim3d(-end,end)
        
        self.draw_joints()
        self.draw_limbs()
        
        self.fig.canvas.draw()

if __name__ == '__main__' :
    pass
    #db.draw_body()
    
#    for i in range(0,len(frames)):
#        db.frame2dof(frames[156])
#        db.cal_global_coord()
#        db.draw_body()
#        time.sleep(1000)
    