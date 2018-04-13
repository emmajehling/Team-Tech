import math
import os
def makematrix(i,j,mtimes,init):
    matrix=[]                           #[[timem1]],[timem2],[timem3]] > time1=[[linej0],[linej1],[linej2]] > line1=[[nodei0],[nodei1],[nodei2]]
    while len(matrix)<mtimes:
        circlines=[]
        while len(circlines)<j:
            radnodes=[]
            while len(radnodes)<i:
                radnodes.append(init)
            circlines.append(radnodes)
        matrix.append(circlines)
    return matrix
def initmatrix():
    i=int(input("Enter the number of radial nodes: "))      #(no index change necessary because that number of indicies will be appended)
    j=int(input("Enter the number of circumferential lines: "))
    mNotOK=True
    while mNotOK:
        m=int(input("Enter the number of time stamps: "))   #must be 3 or greater
        if m>=3:
            mNotOK=False
        else:
            print('________')
            print("must have 3 or more time stamps... Try again:")
    init=316.5    #inital temperature at time 0       #int(input("Enter the initial value for each element: "))
    model=makematrix(i,j,m,init)
    #print("Time 0:")      #displays matrix before any calculations occur
    #showdata(model)
    return model

def showdata(data):
    for timestamp in data:
        print(timestamp)

def showtemp(i,j,m,data):   #prints temperature at node i,j at time m from data matrix (because backwards)
    print(data[m][j][i])

def showcalcs(a,b,c,d,e):
    print('A: ',end='')
    print(a)
    print('B: ',end='')
    print(b)
    print('C: ',end='')
    print(c)
    print('D: ',end='')
    print(d)
    print('E: ',end='')
    print(e)    #displays each calculated term in the equation (used for trouble-shooting)

def radius(i):          #calculate r(i)
    return i*.002
def temp(i,j,m,data):      #finds T(i,j,m) from data to use in formula for Tijm+1
    return data[m][j][i]
def calch(j):
    if j==0:
        return 76.125
    elif j==1:
        return 64.70625
    elif j==2:
        return 15.225
    elif j==3:
        return 38.0625
    elif j==4:
        return 66.609375
    #theta=((2*math.pi)/9)*j
    #return 75*((1-(theta/90))**3)          #inserts appropriate h value for each circumferential line

def innerringtemp(i,j,m,data,t):
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=0.6906187709*(temp(i,jminus1,m,data)+temp(i,jplus1,m,data)-(2*temp(i,j,m,data)))
    b=2.35619449*(temp(i+1,j,m,data)-temp(i,j,m,data))
    c=609.9559217/t
    newtemp=((a+b)/c)+temp(i,j,m,data)
    return newtemp

def nxtyogtemp(i,j,m,data,t):
    #use intermediate equation with milk properties
    jplus1=j+1
    jminus1=j-1
    if i in [0,1,2,4,5,6,7]:    #remove i-1 term for everything up to and including i=7
        e=0
    else:
        e=temp(i-1,j,m,data)*((157.0796325*radius(i-1))-.157096327)
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=temp(i,j,m,data)*((-.0025783101*(1/(radius(i))))-(698.1317008*(radius(i)))-(5421.830415*(radius(i))*(1/t)))
    b=temp(i,jplus1,m,data)*(.001289155*(1/radius(i)))
    c=temp(i,jminus1,m,data)*(.001289155*(1/radius(i)))
    d=temp(i+1,j,m,data)*((157.0796325*radius(i+1))+.157096327)
    newtemp=(a+b+c+d+e)/(-5421.830415*radius(i)*(1/t))
    #showcalcs(a,b,c,d,e) #only used for trouble-shooting
    return newtemp

def nxtglasstemp(i,j,m,data,t):
    #use intermediate equation with glass properties
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=temp(i,j,m,data)*((-.0060160568*(1/(radius(i))))-(698.1317008*(radius(i)))-(2792.526803*(radius(i))*(1/t)))
    b=temp(i,jplus1,m,data)*(.0030080284*(1/radius(i)))
    c=temp(i,jminus1,m,data)*(.0030080284*(1/radius(i)))
    d=temp(i+1,j,m,data)*((366.5191429*radius(i+1))+.3665191429)
    e=temp(i-1,j,m,data)*((366.5191429*radius(i-1))-.3665191429)
    newtemp=(a+b+c+d+e)/(-2792.526803*radius(i)*(1/t))
    #showcalcs(a,b,c,d,e)  #only used for trouble-shooting
    return newtemp

def nxtboundtemp(j,m,data,t): #no i parameter necessary because i=16 on every boundary
    #use boundary condition equation
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=6.098878538*calch(j)
    b=temp(16,j,m,data)*( (.0223402144*calch(j)) -22.5282162-(89.3608577/t))
    c=temp(16,jplus1,m,data)*.0940008883
    d=temp(16,jminus1,m,data)*.0940008883
    e=temp(15,j,m,data)*10.62905514
    newtemp=(a+b+c+d+e)/(-89.3608577/t)
    #showcalcs(a,b,c,d,e)  #only used for trouble-shooting
    return newtemp

def runmodel(data,t):
    m=0
    while m<len(data)-1:  #for each time step (of length t)
        j=0
        while j<len(data[m]): #start from line 0
            i=0                 #start from radius 0.014 (r7) to increase internal volume
            while i<len(data[m][j]):    #calculate each new temp out from center, then repeat on next line, 20 degrees away from center (2 next)
                #calculate temperature at that node for the next time step
                if i in [0,1,2,3,4,5,6]:
                    data[m+1][j][i]='-'
                if i==7:
                    data[m+1][j][i]=innerringtemp(i,j,m,data,t)
                if i in [8,9,10,11,12,13]:
                    #use intermediate equation with milk properties to calculate next time's temperature
                    data[m+1][j][i]=nxtyogtemp(i,j,m,data,t)
                    #print("yogurt")
                elif i in [14,15]:
                    #use intermediate equation with glass properties to calculate next time's temperature
                    data[m+1][j][i]=nxtglasstemp(i,j,m,data,t)
                    #print("glass")
                elif i==16: #node 17
                    #use boundary condition equation to calculate next time's temperature
                    data[m+1][j][i]=nxtboundtemp(j,m,data,t)  #no i parameter necessary because i=16 on every boundary
                    #print("boundary")
                i+=1
            j+=1
        m+=1
    return data         #don't use until fix center problem

def main():
    blankmatrix=initmatrix()
    t=int(input("Enter length of time each time step: "))
    finishedmodel=runmodel(blankmatrix,t)
    print("________")
    print("Completed model:")
    for timestamp in finishedmodel:     #displays modeled data
        print(timestamp)
    exportdata(finishedmodel,t)

def exportdata(data,timestep):
    name=input("Enter file name: ") #different name every time!!
    while os.path.isfile(name+'.csv'):       #returns True if there is a file with this name
        name=input("Name already used. \nTry a different name: ")  #prompts for a new name until it's not used
    thefile=open(name+'.csv',"w")
    m=0
    while m<len(data):    #for each timestep, create a table
        thefile.write('time: '+str((m)*timestep)+' seconds\n')   #except for time 0, each time step labeled on top
        thefile.write(',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16')  #i-value labels
        thefile.write('\n') #new line
        j=0
        while j<len(data[m]):  #each j value is on a different line   for i in range...
            thefile.write(str(j)+',')    #first column is j-value label   #do you need "end" to stop the new line character in file-writing???
            i=0
            while i<len(data[m][j]):
                thefile.write(str(data[m][j][i])+',')    #writes each temperature in order    #do you need "end" stop the new line character in file-writing???
                i+=1
            thefile.write('\n')   #new line once finished with that j-value line
            j+=1
        thefile.write('\n')
        m+=1
    thefile.close()

def test():
    matrix=initmatrix()
    #showdata(matrix)
    print('nxtyogtemp:')
    firsttemp=nxtyogtemp(1,1,0,matrix,5)
    matrix[1][1][1]=firsttemp
    print(firsttemp) #calculates T[i=1,j=1,m=1]
    print(nxtyogtemp(1,1,1,matrix,5))
    print('nxtglasstemp')
    print(nxtglasstemp(14,1,0,matrix,5))  #calculates T[i=14,j=1,m=1]
    print('nxtboundtemp')
    print(nxtboundtemp(1,0,matrix,5)) #calculates T[i=16,j=1,m=1]   #no i parameter necessary because i=16 on every boundary

if __name__=="__main__":
    #test()
    main()
