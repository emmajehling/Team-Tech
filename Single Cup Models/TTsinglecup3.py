import math     #imports python library of functions that make the calculations possible
import os       #imports python library of functions that make exporting to an excel document possible

def makematrix(i,j,mtimes,init):    #the data is stored and edited in nested lists (aka a matrix) and this function creates the matrix
    matrix=[]                           #[[timem1]],[timem2],[timem3]] > time1=[[linej0],[linej1],[linej2]] > line1=[[nodei0],[nodei1],[nodei2]]
    while len(matrix)<mtimes:   #unil every time step has been created, keep creating 'time step' lists (circ lines)
        circlines=[]
        while len(circlines)<j: #until a list for each circumerential line has been created in a time step, keep creating 'line lists' (rad nodes)
            radnodes=[]
            while len(radnodes)<i:  #unil the node at every radial distance has been initialized as one element, keep adding elements (with value "init")
                radnodes.append(init)
            circlines.append(radnodes)
        matrix.append(circlines)
    return matrix   #give this matrix back to the main function to run the model

def glassthickness(mm,r):   #calculates the number of 'glass' nodes, given the distance between nodes and the disired glass thickness
    m=mm/1000       #glass thickness in meters
    ratio=m//r      #divides the glass thickness by the radial distance between nodes, and rounds down
    return ratio    #returns the number of nodes that will 'be glass' (have glass properties)

def radius(i):          #calculates the radius at node i where r(0) starts at 0.014 (for a larger center volume)
    return (i*.002)+.014
def temp(i,j,m,data):      #finds the temperature at a particular node T(i,j,m) from data to use in formula for the next time's temperature Tijm+1
    return data[m][j][i]
def h(j):           #inserts appropriate h value for each circumferential line - these values can be changed for different air speeds
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
def k(i,g,b):         #inserts correct material properties for the particulat node in the formula
    if i in range (0,g):
        return 0.45          #milk k-value
    elif i in range (g,b):
        return 1.05            #glass k-value
def c(i,g,b):           #inserts correct material properties for the particulat node in the formula
    if i in range (0,g):
        return 3770             #milk c-value
    elif i in range (g,b):
        return 800             #glass c-value
def p(i,g,b):           #inserts correct material properties for the particulat node in the formula
    if i in range (0,g):
        return 1030                 #milk p-value
    elif i in range (g,b):
        return 2500             #glass p-value

#the 9 functions below are used to calculate the temperature of a node at the next time step, given the current temperature of that and the surrounding nodes

def generalnodal(i,j,m,data,ct,t,g,b): #used for nodes with indexes i=1-8, j=1-3 (yogurt AND glass nodes not on boundry and not on circumferential edges)
    v=((-2*k(i,g,b)*ct['r'])/(radius(i)*ct['th']))-((2*radius(i)*ct['th'])*k(i,g,b)/ct['r'])+((p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i,g,b)*radius(i)*ct['th'])/ct['r'])+((k(i,g,b)*ct['th'])/2)
    x=((k(i,g,b)*radius(i)*ct['th'])/ct['r'])-((k(i,g,b)*ct['th'])/2)
    y=(k(i,g,b)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((v*temp(i,j,m,data))+(w*temp(i+1,j,m,data))+(x*temp(i-1,j,m,data))+(y*(temp(i,j+1,m,data)+temp(i,j-1,m,data))))/(-z)
    return newtemp

def innerring(i,j,m,data,ct,t,g,b):    #used for nodes with indexes i=0, j=1-3 (nodes on the innermost radial ring and not on the circumferential edges)
    w=((-2*k(i,g,b)*(radius(i)+(ct['r']/2)))/(radius(i)*ct['th']))-((k(i,g,b)*ct['th']*(radius(i)+(ct['r']/2)))/ct['r'])+((p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/(2*t))
    x=(k(i,g,b)*ct['th']*(radius(i)+(ct['r']/2)))/ct['r']
    y=(k(i,g,b)*(radius(i)+(ct['r']/2)))/(radius(i)*ct['th'])
    z=((-p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/(2*t))
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*(temp(i,j+1,m,data)+temp(i,j-1,m,data))))/(-z)
    return newtemp

def outerring(i,j,m,data,ct,t,g,b): #used for nodes with indexes i=9, i=1-3 (nodes on the outermost radial ring and not on the circumferential edges)
    v=((-2*k(i,g,b)*ct['r'])/(radius(i)*ct['th']*2))-(((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=(k(i,g,b)*ct['th']*(radius(i)-(ct['r']/2)))/ct['r']
    x=(k(i,g,b)*ct['r'])/(radius(i)*ct['th']*2)
    y=(-p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t)
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*(temp(i,j+1,m,data)+temp(i,j-1,m,data)))+z)/(-y)
    return newtemp

def leadingcirc(i,j,m,data,ct,t,g,b): #used for nodes with indexes i=1-8, j=0 (yogurt AND glass nodes on leading (closest to the air source) boundry)
    v=((-2*k(i,g,b)*ct['r'])/(radius(i)*ct['th']))-((2*k(i,g,b)*radius(i)*ct['th'])/ct['r'])+((p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    x=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    y=(2*k(i,g,b)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((temp(i,j,m,data)*v)+(temp(i+1,j,m,data)*w)+(temp(i-1,j,m,data)*x)+(temp(i,j+1,m,data)*y))/(-z)
    return newtemp

def endingcirc(i,j,m,data,ct,t,g,b): #used for nodes with indexes i=1-8, j=4 (yogurt AND glass nodes on ending (farthest from the air source) boundry)
    v=((-k(i,g,b)*ct['r'])/(radius(i)*ct['th']))-((2*k(i,g,b)*radius(i)*ct['th'])/ct['r'])+((p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t)
    w=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    x=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    y=(k(i,g,b)*ct['r'])/(radius(i)*ct['th'])
    z=(-p(i,g,b)*c(i,g,b)*radius(i)*ct['th']*ct['r'])/t
    newtemp=((temp(i,j,m,data)*v)+(temp(i+1,j,m,data)*w)+(temp(i-1,j,m,data)*x)+(temp(i,j-1,m,data)*y))/(-z)
    return newtemp

def innermostleadingcirc(i,j,m,data,ct,t,g,b): # used only for node i=0,j=0 (yogurt node on intersection of innermost ring and leading boundry)
    w=(((-2*k(i,g,b))/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2)))-(((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2)))+((p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/t)
    x=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    y=((2*k(i,g,b))/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2))
    z=(-p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/t
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*temp(i,j+1,m,data)))/(-z)
    return newtemp

def outermostleadingcirc(i,j,m,data,ct,t,g,b): #used only for node i=9, j=0 (glass node on intersection of outermost ring and leading boundry)
    v=((-k(i,g,b)*ct['r'])/(radius(i)*ct['th']))-(((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    x=(k(i,g,b)*ct['r'])/(radius(i)*ct['th'])
    y=((-p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*temp(i,j+1,m,data))+z)/(-y)
    return newtemp

def innermostendingcirc(i,j,m,data,ct,t,g,b): #used only for node i=0,j=4 (yogurt node on intersection of innermost ring and ending boundry)
    w=((-k(i,g,b)/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2)))-(((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2)))+((p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/t)
    x=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)+(ct['r']/2))
    y=(k(i,g,b)/(radius(i)*ct['th']))*(radius(i)+(ct['r']/2))
    z=(-p(i,g,b)*c(i,g,b)*ct['th']*((radius(i)+(ct['r']/2))**2))/t
    newtemp=((w*temp(i,j,m,data))+(x*temp(i+1,j,m,data))+(y*temp(i,j-1,m,data)))/(-z)
    return newtemp

def outermostendingcirc(i,j,m,data,ct,t,g,b): #used only for node i=9,j=4 (glass node on intersection of outermost ring and ending boundry)
    v=((-k(i,g,b)*ct['r'])/(2*radius(i)*ct['th']))-(((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2)))-(h(j)*radius(i)*ct['th'])+((p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t))
    w=((k(i,g,b)*ct['th'])/ct['r'])*(radius(i)-(ct['r']/2))
    x=(k(i,g,b)*ct['r'])/(2*radius(i)*ct['th'])
    y=(-p(i,g,b)*c(i,g,b)*ct['th']*ct['r']*((4*radius(i))-ct['r']))/(8*t)
    z=h(j)*radius(i)*ct['th']*ct['Tinf']
    newtemp=((v*temp(i,j,m,data))+(w*temp(i-1,j,m,data))+(x*temp(i,j-1,m,data))+z)/(-y)
    return newtemp

#systematically goes through every nodel in every time step and uses the appropriate equation/function above to calculate the temperature at the next time step
def runmodel(data,ct,t,g,b):    #[g is the first node in the specified glass region and b is one more than the last node (for k, c, p functions)]
    m=0     #start from time 0 seconds (where every node is the specified inital temperature)
    while m<len(data)-1:  #for each time step (of length t), calculate the temperatures of each node at the next time step
        j=0     #start from circumferential line 0
        while j<len(data[m]): #for each circumferential line, calculate the new temperature of each node in order (of radius)
            i=0     #start from radial ring 0
            while i<len(data[m][j]):   #use the appropriate equation/function to calculate the temp. of that node at the next time step, and save this value in the data matrix
                if i in [1,2,3,4,5,6,7,8] and j in [1,2,3]: #ALL nodes not on boundary
                    data[m+1][j][i]=generalnodal(i,j,m,data,ct,t,g,b)
                elif i==0 and j in [1,2,3]: #innermost ring equation
                    data[m+1][j][i]=innerring(i,j,m,data,ct,t,g,b)
                elif i==9 and j in [1,2,3]: #outermost ring equation
                    data[m+1][j][i]=outerring(i,j,m,data,ct,t,g,b)
                elif i in [1,2,3,4,5,6,7,8] and j==0:   #leading circumferential position
                    data[m+1][j][i]=leadingcirc(i,j,m,data,ct,t,g,b)
                elif i in [1,2,3,4,5,6,7,8] and j==4:    #ending circumferential position
                    data[m+1][j][i]=endingcirc(i,j,m,data,ct,t,g,b)

                elif i==0 and j==0:
                    data[m+1][j][i]=innermostleadingcirc(i,j,m,data,ct,t,g,b)
                elif i==9 and j==0:
                    data[m+1][j][i]=outermostleadingcirc(i,j,m,data,ct,t,g,b)
                elif i==0 and j==4:
                    data[m+1][j][i]=innermostendingcirc(i,j,m,data,ct,t,g,b)
                elif i==9 and j==4:
                    data[m+1][j][i]=outermostendingcirc(i,j,m,data,ct,t,g,b)
                i+=1
            j+=1
        m+=1
    return data

def exportdata(data,timestep):   #once the model is finished in python, creates a csv (comma separated values) file of the data (can be opened, saved, and edited in Excel)
    name=input("Enter table-formatted file name: ") #Prompts user for a file name (must have different name every time!!)
    while os.path.isfile(name+'.csv'):       #returns True if there is a file with this name
        name=input("Name already used. \nTry a different name: ")  #prompts for a new name until it's not used
    thefile=open(name+'.csv',"w")   #creates this new "csv" file and opens it for "writing"
    m=0
    while m<len(data):    #for each timestep, create a table for the temperatures
        thefile.write('time: '+str((m)*timestep)+' seconds\n')   #label each time step table with the number of seconds that have been modeled
        thefile.write(',0,1,2,3,4,5,6,7,8,9')  #write one line that labels the radius indexes (i-values)
        thefile.write('\n') #new line
        j=0
        while j<len(data[m]):  #each circumferential line (j value) is on a different line
            thefile.write(str(j)+',')    #first column is labeled by the line index (j-value)
            i=0
            while i<len(data[m][j]):
                thefile.write(str(data[m][j][i])+',')    #writes each temperature in order
                i+=1
            thefile.write('\n')   #new line once finished with that j-value line
            j+=1
        thefile.write('\n')
        m+=1
    thefile.close()     #closes/saves the file as a .csv in the same folder as the python program.
#This file is saved as .csv in the same folder as the python program. It can be opened in Excel, but must be saved as an Excel Workbook for any Excel edits to be saved.

def exportdatatograph(data,timestep,freq):   #once the model is finished in python, creates a csv (comma separated values) file of the data (can be opened, saved, and edited in Excel)
    name=input("Enter graphing file name: ") #Prompts user for a file name (must have different name every time!!)
    while os.path.isfile(name+'.csv'):       #returns True if there is a file with this name
        name=input("Name already used. \nTry a different name: ")  #prompts for a new name until it's not used
    thefile=open(name+'.csv',"w")   #creates this new "csv" file and opens it for "writing"
    thefile.write('seconds')
    j=0
    while j<len(data[0]):   #length will always be 5
        i=0
        while i<len(data[0][j]):    #length with always be 10
            thefile.write(',Node '+str(j)+str(i))    #labels the top line with node references "ji"
            i+=1
        j+=1
    thefile.write('\n')   #new line once finished with that labeling row
    m=0
    while m<len(data): #each row is a different time step
        thefile.write(str(m))   #label first column of each row with the number of seconds
        j=0
        while j<len(data[m]):
            i=0
            while i<len(data[m][j]):
                thefile.write(','+str(data[m][j][i]))
                i+=1
            j+=1
        thefile.write('\n')     #new line once finished with that time step line
        m+=freq
    thefile.close() #closes/saves the file as a .csv in the same folder as the python program.
    #This file is saved as .csv in the same folder as the python program. It can be opened in Excel, but must be saved as an Excel Workbook for any Excel edits to be saved.


def main(): #This is the main function that asks the user to specify details about the model and starts the program
    #initialize matrix
    #specifying the number of nodes, circumerential lines, time steps, and the initial tempurature

    i=int(input("Enter the number of radial nodes (usually 10): "))      #(no index change necessary because that number of indicies will be appended)
    j=int(input("Enter the number of circumferential lines (usually 5): "))
    mNotOK=True     #boolean flag to indicate if the minimum number of time steps specified
    m=int(input("Enter the number of time steps (4 hours is 14400 seconds): "))+1   #(+1 so that the time 0 is the first time step)
    while mNotOK:   #while less than the minimum number of time steps entered
        if m>=3:        #force re-try if less than 3 time steps entered, must be 3 or greater for program to run due to the way it calculates
            mNotOK=False
        else:
            print('________')
            print("must have 3 or more time stemps... Try again:")
    init=float(input("Enter the initial temperature in Fahrenheit (usually 110.03): "))    #specify the initial tempurature at time 0
    kinit=(init+459.67)/(9/5)   #convert entered temperature to Kelvin
    blankmatrix=makematrix(i,j,m,kinit)  #call additional function (at top of program) to create the matrix of data

    #Specify additional constsants
    t=1    #delta t, time between time steps
    ct = {'r':.002,'th':(2*math.pi)/9,} #delta r and delta theta constants (K,C,P values actually pulled from functions at top for simpler reading)
    temp=float(input("Enter ambient temperature in Fahrenheit (usually 31.73): "))  #specify the tempurature of the blowing air (ambient tempurature)
    ktemp=(temp+459.67)/(9/5)   #convert entered temperature to Kelvin
    ct['Tinf']=ktemp       #adds ambient tempurature entry to constants dictionary

    #Specify thickness of glass jar (and therefore volume of yogurt). Total diameter of the cylinder is .064 meters, which is currently not editable
    thickness=int(input("Enter desired glass thickness in millimeters (usually 4mm): "))
    nodes=glassthickness(thickness,ct['r'])    #returns the number of nodes that will 'be glass' (have glass properties)
    g=int(i-nodes)   #first node in glass region - passed to every function as an argument for k, c, p functions

    finishedmodel=runmodel(blankmatrix,ct,t,g,i)    #runs the model!
    freq=int(input("For the 'graphing' file, enter the frequency of data points to be output in seconds: "))
    exportdata(finishedmodel,t)     #saves the model as a csv file that can be opened in Excel. Must be saved as an Excel Workbook for Excel edits to be saved
    exportdatatograph(finishedmodel,t,freq)

if __name__=="__main__":    #calls the main function when the program is run in python
    main()
