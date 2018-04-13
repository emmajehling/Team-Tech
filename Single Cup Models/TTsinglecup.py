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
    i=int(input("Enter the number of radial nodes (usually 10): "))      #(no index change necessary because that number of indicies will be appended)
    j=int(input("Enter the number of circumferential lines (usually 5): "))
    mNotOK=True
    while mNotOK:
        m=int(input("Enter the number of time stamps: "))+1   #so that the time 0 is the first time step
        if m>=3:        #must be 3 or greater
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

def radius(i):          #calculate r(i) where r(0) starts at 0.014
    return (i*.002)+.014
def temp(i,j,m,data):      #finds T(i,j,m) from data to use in formula for Tijm+1
    return data[m][j][i]
def calch(j):           #inserts appropriate h value for each circumferential line
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

def innerringtemp(i,j,m,data,con,t):
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=(con['Kmilk']/(.014*con['Dth']))*(.014+(con['Dr']/2))*(temp(i,jminus1,m,data)+temp(i,jplus1,m,data)-(2*temp(i,j,m,data)))
    b=((con['Kmilk']*con['Dth'])/con['Dr'])*(.014+(con['Dr']/2))*(temp(i+1,j,m,data)-temp(i,j,m,data))
    c=((con['Pmilk']*con['Cmilk']*con['Dth'])*((.014+(con['Dr']/2))**2))/t
    newtemp=((a+b)/c)+temp(i,j,m,data)
    return newtemp

def nxtyogtemp(i,j,m,data,con,t):
    #use intermediate equation with milk properties
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=temp(i,j,m,data)*(((2*con['Kmilk']*con['Dr'])/(radius(i)*con['Dth']))
    -((2*radius(i)*con['Dth'])/con['Dr'])-((con['Pmilk']*con['Cmilk']*radius(i)*con['Dth']*con['Dr'])/t))
    b=temp(i,jplus1,m,data)*((con['Kmilk']*con['Dr'])/(radius(i)*con['Dth']))
    c=temp(i,jminus1,m,data)*((con['Kmilk']*con['Dr'])/(radius(i)*con['Dth']))
    d=temp(i+1,j,m,data)*(((con['Kmilk']*radius(i+1)*con['Dth'])/con['Dr'])+((con['Kmilk']*con['Dth'])/2))
    e=temp(i-1,j,m,data)*(((con['Kmilk']*radius(i-1)*con['Dth'])/con['Dr'])-((con['Kmilk']*con['Dth'])/2))
    newtemp=(a+b+c+d+e)/((con['Pmilk']*con['Cmilk']*radius(i)*con['Dth']*con['Dr'])/t)
    #showcalcs(a,b,c,d,e) #only used for trouble-shooting
    return newtemp

def nxtglasstemp(i,j,m,data,con,t):
    #use intermediate equation with glass properties
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=temp(i,j,m,data)*(((2*con['Kglass']*con['Dr'])/(radius(i)*con['Dth']))-((2*radius(i)*con['Dth'])/con['Dr'])
    -((con['Pglass']*con['Cglass']*radius(i)*con['Dth']*con['Dr'])/t))
    b=temp(i,jplus1,m,data)*((con['Kglass']*con['Dr']) / (radius(i)*con['Dth'])  )
    c=temp(i,jminus1,m,data)*(  (con['Kglass']*con['Dr']) / (radius(i)*con['Dth'])  )
    d=temp(i+1,j,m,data)*(  ((con['Kglass']*radius(i+1)*con['Dth'])/con['Dr'])  +  ((con['Kglass']*con['Dth'])/2)  )
    e=temp(i-1,j,m,data)*(  ((con['Kglass']*radius(i-1)*con['Dth'])/con['Dr'])  -  ((con['Kglass']*con['Dth'])/2)  )
    newtemp=(a+b+c+d+e)/((con['Pglass']*con['Cglass']*radius(i)*con['Dth']*con['Dr'])/t)
    #showcalcs(a,b,c,d,e)  #only used for trouble-shooting
    return newtemp

def nxtboundtemp(j,m,data,con,t): #no i parameter necessary because i=16 on every boundary
    #use boundary condition equation
    R=0.032
    jplus1=j+1
    jminus1=j-1
    if j==0:
        jminus1=1  #line 0's j-1 is 1 because the nonincluded -40 degree line is reflected over line 0
    elif j==4:
        jplus1=j   #line 4's j+1 is itself because it is reflected over the 180 degree line
    a=calch(j)*R*con['Dth']*con['Tinf']
    b=temp(9,j,m,data)*((calch(j)*R*con['Dth'])-((2*con['Kglass']*con['Dr'])/(R*con['Dth']))
    -((2*R*con['Dth'])/(con['Dr']))-((con['Pglass']*con['Cglass']*R*con['Dth']*con['Dr'])/t))
    c=temp(9,jplus1,m,data)*((con['Kglass']*con['Dr'])/(R*con['Dth']))
    d=temp(9,jminus1,m,data)*((con['Kglass']*con['Dr'])/(R*con['Dth']))
    e=temp(8,j,m,data)*(((con['Kglass']*radius(8)*con['Dth'])/con['Dr'])-((con['Kglass']*con['Dth'])/2))
    newtemp=(a+b+c+d+e)/((con['Pglass']*con['Cglass']*R*con['Dth']*con['Dr'])/t)
    #showcalcs(a,b,c,d,e)  #only used for trouble-shooting
    return newtemp

def runmodel(data,con,t):
    m=0
    while m<len(data)-1:  #for each time step (of length t)
        j=0
        while j<len(data[m]): #start from line 0
            i=0                 #start from radius 0.014 (r7) to increase internal volume
            while i<len(data[m][j]):    #calculate each new temp out from center, then repeat on next line, 20 degrees away from center (2 next)
                #calculate temperature at that node for the next time step
                if i==0:
                    data[m+1][j][i]=innerringtemp(i,j,m,data,con,t)
                if i in [1,2,3,4,5,6]:         #use intermediate equation with milk properties to calculate next time's temperature
                    data[m+1][j][i]=nxtyogtemp(i,j,m,data,con,t)
                elif i in [7,8]:              #intermediate equation with glass properties to calculate next time's temperature
                    data[m+1][j][i]=nxtglasstemp(i,j,m,data,con,t)
                elif i==9: #outer ring         boundary condition equation to calculate next time's temperature
                    data[m+1][j][i]=nxtboundtemp(j,m,data,con,t)  #no i parameter necessary because i=16 on every boundary
                i+=1
            j+=1
        m+=1
    return data

def exportdata(data,timestep):
    name=input("Enter file name: ") #different name every time!!
    while os.path.isfile(name+'.csv'):       #returns True if there is a file with this name
        name=input("Name already used. \nTry a different name: ")  #prompts for a new name until it's not used
    thefile=open(name+'.csv',"w")
    m=0
    while m<len(data):    #for each timestep, create a table
        thefile.write('time: '+str((m)*timestep)+' seconds\n')   #except for time 0, each time step labeled on top
        thefile.write(',0,1,2,3,4,5,6,7,8,9')  #i-value labels
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

def main():
    blankmatrix=initmatrix()
    t=int(input("Enter length of time each time step in seconds (no more than 30): "))
    con = {           #constants
    'Dr':.002,
    'Dth':(2*math.pi)/9,
    'Kglass':1.05,
    'Pglass':2500,
    'Cglass':800,
    'Kmilk':0.45,
    'Pmilk':1030,
    'Cmilk':3770,
    'Tinf':273       #ambient temperature or temperature of air blown on yogurt cup
    }
    finishedmodel=runmodel(blankmatrix,con,t)
    exportdata(finishedmodel,t)

if __name__=="__main__":
    main()
