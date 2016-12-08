'''
read from given .amc file, output a dictionary of root+bonedata
'''
def read(path, cnt):
    file_name = path
    f = open(file_name)
    line = f.readline()
    line = line.strip()
    frames = []#a dictionary contains data for all frames
    #skip line start with "#" and ":"
    while (not line.isdigit()):
        line = f.readline()
        line = line.strip()

    frame_cnt = 0
    while line and frame_cnt < cnt:
        #a new frame comes
        if line.isdigit():
            temp_frame = {}
            line = f.readline()
            line = line.strip()
            while line and (not line.isdigit()):
                #stay with current frame
                #there is no lhipjoint nor rhipjoint
                tmp = line.split(" ")
                tmp = filter(None, tmp)
                temp_frame[tmp[0]] = tmp[1:]
                line = f.readline()
                line = line.strip()
            #print temp_frame
            #sys.exit()
            frames.append(temp_frame)
            frame_cnt += 1
        else:
            line = f.readline()
            line = line.strip()
    f.close()
    return frames

if __name__ == '__main__' :
    frames = read("19_08.amc",5)
    
