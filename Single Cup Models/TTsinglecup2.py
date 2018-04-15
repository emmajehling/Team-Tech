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

#def glassthickness(mm,r):   #calculates the number of 'glass' nodes, given the distance between nodes and the disired glass thickness
    #m=mm/1000       #glass thickness in meters
    #ratio=m//r      #divides the glass thickness by the radial distance between nodes, and rounds down
    #return ratio    #returns the number of nodes that will 'be glass' (have glass properties)
#def changeregions(firstglass):
    #somehow change k, c, p functions...


def radius(i):          #calculate r(i) where r(0) starts at 0.014
    return (i*.002)+.014
def temp(i,j,m,data):      #finds T(i,j,m) from data to use in formula for Tijm+1
    return data[m][j][i]
def h(j):           #inserts appropriate h value for each circumferential line
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
def k(i):
    if i in [0,1,2,3,4,5,6,7]:    #range (0,g):
        return 0.45          #milk k-value
    elif i in [8,9]:        #range (g,10)
        return 1.05            #glass k-value        #material properties
def c(i):
    if i in [0,1,2,3,4,5,6,7]:                      #range (0,g):
        return 3770             #milk c-value
    elif i in [8,9]:                                #range (g,10):
        return 800             #glass c-value         #material properties
def p(i):
    if i in [0,1,2,3,4,5,6,7]:                  #range (0,g):
        return 1030                 #milk p-value
    elif i in [8,9]:                            #range (g,10):
        return 2500             #glass p-value        #material properties

def generalnodal(i,j,m,data,ct,t): #i=1-8, j=1-3 (milk AND glass nodes not on boundry)
    v=((-2*k(i)*ct['r'])/(radius(i)*ct['th']))-((2*radius(i)*ct['th'])*k(i)/ct['r'])+((p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i)*radius(i)*ct['th'])/ct['r'])+((k(i)*ct['th'])/2)
    x=((k(i)*radius(i)*ct['th'])/ct['r'])-((k(i)*ct['th'])/2)
    y=(k(i)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((v*temp(i,j,m,data))+(w*temp(i+1,j,m,data))+(x*temp(i-1,j,m,data))+(y*(temp(i,j+1,m,data)+temp(i,j-1,m,data))))/(-z)
    return newtemp

def innerring(i,j,m,data,ct,t):    #i=0, j=1-3
    w=((-2*k(i)*(radius(i)+(ct['r']/2)))/(radius(i)*ct['th']))-((k(i)*ct['th']*(radius(i)+(ct['r']/2)))/ct['r'])+((p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/(2*t))
    x=(k(i)*ct['th']*(radius(i)+(ct['r']/2)))/ct['r']
    y=(k(i)*(radius(i)+(ct['r']/2)))/(radius(i)*ct['th'])
    z=((-p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/(2*t))
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*(temp(i,j+1,m,data)+temp(i,j-1,m,data))))/(-z)
    return newtemp

def outerring(i,j,m,data,ct,t): #i=9, i=1-3
    v=((-2*k(i)*ct['r'])/(radius(i)*ct['th']*2))-(((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=(k(i)*ct['th']*(radius(i)-(ct['r']/2)))/ct['r']
    x=(k(i)*ct['r'])/(radius(i)*ct['th']*2)
    y=(-p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t)
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*(temp(i,j+1,m,data)+temp(i,j-1,m,data)))+z)/(-y)
    return newtemp

def leadingcirc(i,j,m,data,ct,t): #i=1-8, j=0 (milk AND glass nodes on leading boundry)
    v=((-2*k(i)*ct['r'])/(radius(i)*ct['th']))-((2*k(i)*radius(i)*ct['th'])/ct['r'])+((p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    x=((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    y=(2*k(i)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((temp(i,j,m,data)*v)+(temp(i+1,j,m,data)*w)+(temp(i-1,j,m,data)*x)+(temp(i,j+1,m,data)*y))/(-z)
    return newtemp

def endingcirc(i,j,m,data,ct,t): #i=1-8, j=4 (milk AND glass nodes on ending boundry)
    v=((-k(i)*ct['r'])/(radius(i)*ct['th']))-((2*k(i)*radius(i)*ct['th'])/ct['r'])+((p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    x=((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    y=(k(i)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i)*c(i)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((temp(i,j,m,data)*v)+(temp(i+1,j,m,data)*w)+(temp(i-1,j,m,data)*x)+(temp(i,j-1,m,data)*y))/(-z)
    return newtemp

def innermostleadingcirc(i,j,m,data,ct,t): #i=0,j=0
    w=(((-2*k(i))/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2)))-(((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2)))+((p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/t)
    x=((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    y=((2*k(i))/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2))
    z=(-p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/t
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*temp(i,j+1,m,data)))/(-z)
    return newtemp

def outermostleadingcirc(i,j,m,data,ct,t): #i=9, j=0
    v=((-k(i)*ct['r'])/(radius(i)*ct['th']))-(((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    x=(k(i)*ct['r'])/(radius(i)*ct['th'])
    y=((-p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*temp(i,j+1,m,data))+z)/(-y)
    return newtemp

def innermostendingcirc(i,j,m,data,ct,t): #i=0,j=4
    w=((-k(i)/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2)))-(((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2)))+((p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/t)
    x=((k(i)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    y=(k(i)/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2))
    z=(-p(i)*c(i)*ct['th']*((radius(i)+(ct['r']/2))**2))/t
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*temp(i,j-1,m,data)))/(-z)
    return newtemp

def outermostendingcirc(i,j,m,data,ct,t): #i=9,j=4
    v=((-k(i)*ct['r'])/(2*radius(i)*ct['th']))-(((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=((k(i)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    x=(k(i)*ct['r'])/(2*radius(i)*ct['th'])
    y=(-p(i)*c(i)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t)
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*temp(i,j-1,m,data))+z)/(-y)
    return newtemp

def runmodel(data,ct,t):
    m=0
    while m<len(data)-1:  #for each time step (of length t)
        j=0
        while j<len(data[m]): #start from line 0
            i=0                 #start from radius 0.014 (r7) to increase internal volume
            while i<len(data[m][j]):    #calculate each new temp out from center, then repeat on next line, 20 degrees away from center (2 next), then assign that to correct list element
                if i in [1,2,3,4,5,6,7,8] and j in [1,2,3]: #ALL nodes not on boundary
                    data[m+1][j][i]=generalnodal(i,j,m,data,ct,t)
                elif i==0 and j in [1,2,3]: #innermost ring equation
                    data[m+1][j][i]=innerring(i,j,m,data,ct,t)
                elif i==9 and j in [1,2,3]: #outermost ring equation
                    data[m+1][j][i]=outerring(i,j,m,data,ct,t)
                elif i in [1,2,3,4,5,6,7,8] and j==0:   #leading circumferential position
                    data[m+1][j][i]=leadingcirc(i,j,m,data,ct,t)
                elif i in [1,2,3,4,5,6,7,8] and j==4:    #ending circumferential position
                    data[m+1][j][i]=endingcirc(i,j,m,data,ct,t)

                elif i==0 and j==0:
                    data[m+1][j][i]=innermostleadingcirc(i,j,m,data,ct,t)
                elif i==9 and j==0:
                    data[m+1][j][i]=outermostleadingcirc(i,j,m,data,ct,t)
                elif i==0 and j==4:
                    data[m+1][j][i]=innermostendingcirc(i,j,m,data,ct,t)
                elif i==9 and j==4:
                    data[m+1][j][i]=outermostendingcirc(i,j,m,data,ct,t)
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
        thefile.write('time: '+str((m)*timestep)+' secds\n')   #each time step labeled on top
        thefile.write(',0,1,2,3,4,5,6,7,8,9')  #i-value labels
        thefile.write('\n') #new line
        j=0
        while j<len(data[m]):  #each j value is on a different line
            thefile.write(str(j)+',')    #first column is j-value label
            i=0
            while i<len(data[m][j]):
                thefile.write(str(data[m][j][i])+',')    #writes each temperature in order
                i+=1
            thefile.write('\n')   #new line once finished with that j-value line
            j+=1
        thefile.write('\n')
        m+=1
    thefile.close()

def main():
    #initialize matrix
    #specifying the number of nodes, circumerential lines, time steps, and the initial tempurature
    i=int(input("Enter the number of radial nodes (usually 10): "))      #(no index change necessary because that number of indicies will be appended)
    j=int(input("Enter the number of circumferential lines (usually 5): "))
    mNotOK=True     #boolean flag to indicate if the minimum number of time steps specified
    m=int(input("Enter the number of time steps: "))+1   #(+1 so that the time 0 is the first time step)
    while mNotOK:   #while less than the minimum number of time steps entered
        if m>=3:        #force re-try if less than 3 time steps entered, must be 3 or greater for program to run due to the way it calculates
            mNotOK=False
        else:
            print('________')
            print("must have 3 or more time stemps... Try again:")
    init=float(input("Enter the initial tempurature in Kelvin (usually 316.5): "))    #specify the initial tempurature at time 0
    blankmatrix=makematrix(i,j,m,init)  #call additional function (at top of program) to create the matrix of data

    #Specify additional constsants
    t=int(input("Enter length of time each time step in seconds (no more than 30): "))    #delta t, time between time steps
    ct = {'r':.002,'th':(2*math.pi)/9,} #delta r and delta theta constants (K,C,P values actually pulled from functions at top for simpler reading)
    temp=float(input("Enter ambient temperature in Fahrenheit (usually 273): "))    #specify the tempurature of the blowing air (ambient tempurature)
    ct['Tinf']=temp       #adds ambient tempurature entry to constants dictionary

    #Specify thickness of glass jar (and therefore volume of yogurt). Total diameter of the cylinder is .064 meters
    #thickness=int(input("Enter desired glass thickness in millimeters: "))
    #gt=glassthickness(thickness,ct['r'])    #returns the number of nodes that will 'be glass' (have glass properties)
    #firstglassnode=i-gt   #first node in glass region
    #changeregions(firstglassnode)   #changes which nodes use yogurt and glass properties in the p, c, and k functions

    finishedmodel=runmodel(blankmatrix,ct,t)
    exportdata(finishedmodel,t)

if __name__=="__main__":
    main()
