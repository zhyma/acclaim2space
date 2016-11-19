'''
find id by joint name
return -1 if target not found
'''
def find_by_name(name, body):
    for i in range(0,len(body)):
        if body[i]['name'] == name:
            return i
    return -1

'''
arrange all joints into different levels
root is on level 0
then lowerback, hipjoints on level 1, etc
'''
def get_level(body):

    level = [[0]]
    cnt = 0
    level_i = 1
    while cnt < len(body)-1:
        temp = []
        for i in range(1,len(body)):
            if body[i]['parent'] in level[level_i-1]:
                temp.append(i)
                cnt += 1
        level_i += 1
        level.append(temp)
    return level

'''
read from given .asf file, output a dictionary of root+bonedata
'''
def read(path):
    file_name = path
    f = open(file_name)
    line = f.readline()
    body = {}#a dictionary contains all joints
    #skip :version, :name, :units, :documentation
    #find :root
    while line and (':root' not in line):
        #process bonedata
        line = f.readline()
    if ':root' not in line:
        f.close()
        print 'Incomplete file (lack of "root"). Ends here'
        return ''
    #process :root
    root = {}
    while line and (':bonedata' not in line):
        line = f.readline()
        line = line.strip()
        line = line.lower()
        tmp = line.split(' ')
        tmp = filter(None, tmp)
        #usually is all 0
        if 'position' in line:
            root['position'] = [tmp[1],tmp[2],tmp[3]]
        elif 'orientation' in line:
            root['orientation'] = [tmp[1],tmp[2],tmp[3]]
        elif 'order' in line:
            root['dof'] = []
            [root['dof'].append(tmp[i]) for i in range(1,len(tmp))]
    #root['dof'] = ['tx','ty','tz','rx','ry','rz']
    root['name'] = 'root'
    root['parent'] = -1#as root
    body[0] = root
    if ':bonedata' not in line:
        f.close()
        print 'Incomplete file (lack of "bonedata"). Ends here'
        return ''
    #process bonedata
    while line and (':hierarchy' not in line):
        line = f.readline()
        #find one joint
        if 'begin' in line:
            joint = {}
            tmp_id = 0#id
            joint['name'] = ''
            joint['dir'] = []
            joint['axis'] = []
            joint['dof'] = []
            joint['parent'] = ''
            while line and ('end' not in line):
                line = f.readline()
                line = line.strip()
                tmp = line.split(' ')
                tmp = filter(None, tmp)
                if 'id' in line:
                    tmp_id = int(tmp[1])
                elif 'name' in line:
                    joint['name'] = tmp[1]
                elif 'direction' in line:
                    joint['dir'] = [float(tmp[1]),float(tmp[2]),float(tmp[3])]
                elif 'length' in line:
                    joint['len'] = float(tmp[1])
                elif 'axis' in line:
                    joint['axis'] = [float(tmp[1]),float(tmp[2]),float(tmp[3])]
                elif 'dof' in line:
                    for i in range(1,len(tmp)):
                        joint['dof'].append(tmp[i])
            if not line:
                f.close()
                print 'Incomplete file (error in "bonedata"). Ends here'
                return ''
            else:
                body[tmp_id] = joint
    if ':hierarchy' not in line:
        f.close()
        print 'Incomplete file (lack of "hierarchy"). Ends here'
        return ''
    #process hierarchy structure
    while line:
        line = f.readline()
        if 'begin' in line:
            while line and ('end' not in line):
                line = f.readline()
                line = line.strip()
                tmp = line.split(' ')
                tmp = filter(None, tmp)
                for i in range(1,len(tmp)):#root==0 is not included
                    child = find_by_name(tmp[i], body)
                    parent = find_by_name(tmp[0], body)
                    if child!=-1 and parent != -1:
                        body[child]['parent'] = parent
                    else:
                        print 'Hierarchy Error at: ' + line
            if not line:
                f.close()
                print 'Incomplete file (error in "hierarchy"). Ends here'
                return ''
            else:
                f.close()
                print 'Read ' + path + ' done!'
                return body
        else:
            f.close()
            print 'Incomplete file. Ends here'
            return ''
    f.close()
    print 'Incomplete file. Ends here'
    return ''

if __name__ == '__main__' :
    body = read('19.asf')
    level = get_level(body)
    