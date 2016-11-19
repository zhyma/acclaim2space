import numpy as np
import math
import asf_reader
import amc_reader

class bodyto3d:
    '''
    Initialize with the path of .asf and .amc, and maximum frames you want to read.
    Call function "convert" with the serial number of a frame as input parameter
    to convert Euler angles to World Coordinate (Euclid).
    Expect output is an object array: [[float(x),float(y),float(z),int(parent)],...],
    order is according to input .asf file.
    
    The convert() and cal_local_coord() is migrate from
    [Floristt's (floristt@126.com) C++ code](http://www.cnblogs.com/floristt/p/4720080.html)
    The original name of convert() is cal_global_coord().
    '''
    #data from .asf file
    body = {}
    level = []#hierarchy structure
    #data from .amc file
    frames = []

    local_coord = []

    '''
    input: the path of .asf file, the path of amc file, maximum frames to read
    '''
    def __init__(self, asf_path, amc_path, max_frames):
        #read .asf and .amc file
        self.body = asf_reader.read(asf_path)
        self.frames = amc_reader.read(amc_path, max_frames)
        print 'Read ' + str(len(self.frames)) + ' frames.'
        
        self.level = asf_reader.get_level(self.body)
        
        self.local_coord = np.zeros((len(self.body),3))
        self.body[0]['axis'] = [0,0,0]
        self.body[0]['dir'] = [0,0,0]
        self.body[0]['len'] = 0
        self.cal_local_coord()
        
    '''
    from Euler angles to World Coordinate System (calculate global coordinate)
    input: the serial number of a frame (start from 0)
    '''
    def convert(self, num):
        if num > len(self.frames):
            print 'Frame No. ' + str(num) + ' is not within the range of buffer!'
            return
        else:
            print 'Process frame No. ' + str(num) + '.'

        #a joint is (float(x), float(y), float(z), int(parent))
        #joints = np.zeros((len(self.body),4))
        joints = np.zeros((len(self.body),4)).astype(object)
        #joints[:,3] = joints[:,3].astype(int)
        
        #get rotation matrix for all DOFs of all joints
        dof_mat = self.frame2dof(num)
        for i in range(0,len(self.body)):
            temp = self.local_coord[i]
            child_id = i
            parent_id = self.body[i]['parent']
            while child_id != 0:
                rot_x = self.rot_mat(dof_mat[child_id][3],'x')
                temp = np.dot(rot_x,temp)
                rot_y = self.rot_mat(dof_mat[child_id][4],'y')
                temp = np.dot(rot_y,temp)
                rot_z = self.rot_mat(dof_mat[child_id][5],'z')
                temp = np.dot(rot_z,temp)
                
                #define rotation matrix for single axis
                rot_cur_x = self.rot_mat(self.body[child_id]['axis'][0],'x')
                rot_cur_y = self.rot_mat(self.body[child_id]['axis'][1],'y')
                rot_cur_z = self.rot_mat(self.body[child_id]['axis'][2],'z')
                rot_par_x = self.rot_mat(self.body[parent_id]['axis'][0],'x')
                rot_par_y = self.rot_mat(self.body[parent_id]['axis'][1],'y')
                rot_par_z = self.rot_mat(self.body[parent_id]['axis'][2],'z')
                
                #get combined rotation matrix
                rot_mat_cur = np.dot(rot_cur_y,rot_cur_x)
                rot_mat_cur = np.dot(rot_cur_z,rot_mat_cur)
                
                rot_mat_fat = np.dot(rot_par_y,rot_par_x)
                rot_mat_fat = np.dot(rot_par_z,rot_mat_fat)
                
                #migration start
                temp = np.dot(rot_mat_cur,temp)
                
                temp_vec = np.zeros(3)
                temp_vec[0] = self.body[parent_id]['len']*self.body[parent_id]['dir'][0]
                temp_vec[1] = self.body[parent_id]['len']*self.body[parent_id]['dir'][1]
                temp_vec[2] = self.body[parent_id]['len']*self.body[parent_id]['dir'][2]

                temp[0] += temp_vec[0]
                temp[1] += temp_vec[1]
                temp[2] += temp_vec[2]

                temp = np.dot(np.linalg.inv(rot_mat_fat),temp)
                
                child_id = parent_id
                parent_id = self.body[child_id]['parent']
                #end of while
            #rotation and transformation according to root
            rot_x = self.rot_mat(dof_mat[0][3],'x')
            temp = np.dot(rot_x, temp)
            rot_y = self.rot_mat(dof_mat[0][4],'y')
            temp = np.dot(rot_y, temp)
            rot_z = self.rot_mat(dof_mat[0][5],'z')
            temp = np.dot(rot_z, temp)
            temp[0] += dof_mat[0][0]
            temp[1] += dof_mat[0][1]
            temp[2] += dof_mat[0][2]
            joints[i][:3] = temp
            joints[i][3] = int(self.body[i]['parent'])
        return joints

    '''
    read one frame from frames, convert to dof matrix
    '''
    def frame2dof(self, num):
        frame = self.frames[num]
        #initialize/reset dof matrix
        #(tx, ty, tz, rx, ry, rz) for each joints
        dof_mat = np.zeros((len(self.body),6))
        for i in range(0,len(self.body)):
            name = self.body[i]['name']
            #set dof matrix for certain angle
            #hips do not have any dof as default
            if name in frame:
                dof = self.body[i]['dof']
                for j in range(0,len(frame[name])):
                    if dof[j] == 'tx':
                        k = 0
                    elif dof[j] == 'ty':
                        k = 1
                    elif dof[j] == 'tz':
                        k = 2
                    elif dof[j] == 'rx':
                        k = 3
                    elif dof[j] == 'ry':
                        k = 4
                    elif dof[j] == 'rz':
                        k = 5
                    elif dof[j] == 'ty':
                        k = 6
                    else:
                        print 'There is a conflict between the .asf and the .amc file, wrong DOF'
                    dof_mat[i][k] = frame[name][j]
        return dof_mat

    '''
    calculate rotation matrix
    theta is in degrees
    '''
    def rot_mat(self, theta, axis):
        rot = np.zeros((3,3))
        theta = math.radians(theta)
        c = math.cos(theta)
        s = math.sin(theta)
        if axis=='x':
            rot = [[ 1,  0,   0],
                   [ 0,  c,  -s],
                   [ 0,  s,   c]]
        elif axis=='y':
            rot = [[ c,  0,  s],
                   [ 0,  1,  0],
                   [-s,  0,  c]]
        elif axis=='z':
            rot = [[ c, -s,  0],
                   [ s,  c,  0],
                   [ 0,  0,  1]]
        else:
            rot = np.eye(3)
            print 'Axis error?'
        return rot

    '''
    calculate local coordinate
    '''
    def cal_local_coord(self):
        #calculate local coordinate
        for i in range(1,len(self.body)):
            self.local_coord[i][0] = self.body[i]['len']*self.body[i]['dir'][0]#x
            self.local_coord[i][1] = self.body[i]['len']*self.body[i]['dir'][1]#y
            self.local_coord[i][2] = self.body[i]['len']*self.body[i]['dir'][2]#z

        #rotate z-y-x
        for i in range(1,len(self.body)):
            rot_z = self.rot_mat(-self.body[i]['axis'][2],'z')
            self.local_coord[i] = np.dot(rot_z,self.local_coord[i])#z
            rot_y = self.rot_mat(-self.body[i]['axis'][1],'y')
            self.local_coord[i] = np.dot(rot_y,self.local_coord[i])#y
            rot_x = self.rot_mat(-self.body[i]['axis'][0],'x')
            self.local_coord[i] = np.dot(rot_x,self.local_coord[i])#x

if __name__ == '__main__' :
    import draw_body as db
    #file from [CMU mocap database](http://mocap.cs.cmu.edu/search.php?subjectnumber=19&trinum=8)
    trans = bodyto3d('19.asf', '19_08.amc', 1000)
    joints = trans.convert(100)
    
    plot = db.draw_body(joints)
    plot.draw()