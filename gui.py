#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *
from project5 import FindItem, FindDistance, TotalCostWithWeight, FindWeight
from project2 import modified_NN
from branch_bound import branch_bound
import copy

#Because of scale and making the GUI looks reasonable,
#I need to make some from transfer the address into the location in canvas
#The map rigt now is: 32*x+24

class GUIforPickOrder(object):
    #This is the init function,
    #it will be implemented once the class object is created
    def __init__(self,master):
        
        #build the canvas to draw all the shelves and path to pick the item
        self.w = Canvas(master, width=700, height=420)
        
        #build the all the elements needed in the canvas
        self.alg = IntVar()
        self.weight = IntVar()
        Radiobutton(master,text='Nearest Neighbor',variable=self.alg, value=0).grid(row = 2, column = 0)
        Radiobutton(master,text='Branch&Bound',variable=self.alg, value=1).grid(row = 2, column = 2)
        
        Radiobutton(master,text='With Weight',variable=self.weight, value=0).grid(row = 3, column = 0)
        Radiobutton(master,text='Without Weight',variable=self.weight, value=1).grid(row = 3, column = 2, pady = 20)
        
        self.StartLabel = Label(master, text = 'Start Address: ')
        self.StartEntry = Entry(master)
        
        #set the default value of entry
        self.StartEntry.insert(10,"0,0")
        self.EndLabel = Label(master, text = 'End Address: ')
        self.EndEntry = Entry(master)
        self.EndEntry.insert(10,"18,0")
        self.OrderLabel = Label(master, text = 'Order: ')
        self.OrderEntry = Entry(master,width = 40)
        self.OrderEntry.insert(10,"1147851,61210,231434,76182,388082,388746,361415,379553,357344,396342,89769,391835,359287,160922,392028,108775,274852,286783")
        #self.OrderEntry.insert(10,"172,610,74")
        #self.OrderEntry.insert(10,"1,45,74,281610,342706,111873,198029,366109,287261,76283,254489,258540,286457")
        self.PathButton = Button(master, text = "Show Path", command = self.ShowOrginPath)
        self.CostLabel = Label(master, text = 'Cost: ')
        self.CostEntry = Entry(master)
        self.OptimalOrderLabel = Label(master, text = 'Optimal Order: ')
        self.OptimalOrderEntry = Entry(master,width = 40)
        self.OptimalPathButton = Button(master, text = "Find Optimal", command = self.FindOptimal)
        self.OptimalCostLabel = Label(master, text = 'Optimal Cost: ')
        self.OptimalCostEntry = Entry(master)
        
        Label(master, text = 'Input File: ').grid(row = 9, column = 0)
        self.InputFileEntry = Entry(master)
        self.InputFileEntry.insert(10,"warehouse-orders-v01.csv")
        
        Label(master, text = 'Output File: ').grid(row = 10, column = 0)
        self.OutputFileEntry = Entry(master)
        self.OutputFileEntry.insert(10,"test.txt")
        
        Button(master, text = "Process File", command = self.ProcessFile).grid(row = 10, column = 2)
        
        Label(master, text = 'Pick Order: ').grid(row = 12, column = 0)
        self.PickOrderEntry = Entry(master)
        Button(master, text = "Pick", command = self.PickOrder).grid(row = 12, column = 2)
        
        Label(master, text = 'Weight Capacity: ').grid(row = 11, column = 0)
        self.WeightCapacity= Entry(master)
        self.WeightCapacity.insert(10,"20")
        self.WeightCapacity.grid(row = 11, column = 1)
        
        #pack all elements to the window
        self.w.grid(row = 0,column=0, rowspan = 2, columnspan = 4)
        self.StartLabel.grid(row = 4, column = 0)
        self.StartEntry.grid(row = 4, column = 1)
        self.EndLabel.grid(row = 4, column = 2)
        self.EndEntry.grid(row = 4, column = 3)
        
        self.OrderLabel.grid(row = 5, column = 0)
        self.OrderEntry.grid(row = 5, column = 1,columnspan = 2)
        self.PathButton.grid(row = 5, column = 3)
        self.CostLabel.grid(row = 6, column = 0)
        self.CostEntry.grid(row = 6, column = 1)
        
        self.OptimalOrderLabel.grid(row = 7, column = 0)
        self.OptimalOrderEntry.grid(row = 7, column = 1)
        self.OptimalPathButton.grid(row = 7, column = 2)
        self.OptimalCostLabel.grid(row = 8, column = 0)
        self.OptimalCostEntry.grid(row = 8, column = 1)
        
        self.InputFileEntry.grid(row = 9, column = 1)
        self.OutputFileEntry.grid(row = 10, column = 1)
        
        self.PickOrderEntry.grid(row = 12, column = 1)
        
        
        '''
        #pack all elements to the window
        self.w.pack()
        self.StartLabel.pack(side = LEFT)
        self.StartEntry.pack(side = LEFT)
        self.EndEntry.pack(side = RIGHT)
        self.EndLabel.pack(side = RIGHT)
        
        self.OrderLabel.pack()
        self.OrderEntry.pack(side = LEFT)
        '''
        #draw the all the rectangles to represent the shelf
        self.shelf = []
        for i in range(20):
            self.shelf.append([])
            for j in range(11):
                self.shelf[i].append(self.w.create_rectangle(32*i+32,32*j+32,32*i+48,32*j+48, fill="yellow"))
    

    #This function can mark the items'location to red in an order
    def MarkItem(self,order):
        for item in order:
            address = FindItem(item)
            if len(address) == 0:
                print ('Error: Item %s does not have an address' %item)
                
                continue
            self.w.itemconfig(self.shelf[int(address[0]-0.5)][int(address[1]-0.5)],fill='red')


    #This function show the path of a worker to pick up the item in an order
    #from start address to end address
    #Also, this funtion will return the total distance of this path
    def ShowPath(self, start, order, end, color):
        start_address = [float(start[0]), float(start[1])]
        distance = 0
        #variable path is used to record all corners' location
        path = [start_address[0]*32+24,start_address[1]*32+24]
        temp_order = copy.copy(order)
        for item in order:
            end_address = FindItem(item)
            temp_order.remove(item)
            #Show the error message
            if len(end_address) == 0:
                print ('Error: Item %s does not have an address' %item)
                continue
            
            if abs(end_address[0]-start_address[0])==0.5 and end_address[1]==start_address[1]:
                #means the worker is currently standing on the right or left side of the target shelf
                print "Don't need to move to pick up %s" %item
                continue
            
            move = 0
            for item2 in temp_order:
                
                temp_address = FindItem(item2)
                
                if end_address[0]-temp_address[0]==1 and end_address[1]==temp_address[1]:
                    #means there is an item in the left shelf of the target shelf
                    move = -1
                    break
                elif end_address[0]-temp_address[0]==-1 and end_address[1]==temp_address[1]:
                    #means there is an item in the right shelf of the target shelf
                    move = 1
                    break
                
            
            distance = distance + FindDistance(start_address,end_address)
            #Means worker is stand by a shelf right now
            #then the worker will move 0.5 unit of distance
            #Direction depends on the relative location between current location and goal
            if (2*start_address[1])%2==1:
                if start_address[1] <= end_address[1]:
                    start_address[1] = start_address[1] + 0.5
                else:
                    start_address[1] = start_address[1] - 0.5
                path.append(start_address[0]*32+24)
                path.append(start_address[1]*32+24)
                
            
            #This represents worker walk from current address to the goal
            if start_address[0] < end_address[0]:
                start_address[0] = end_address[0]-0.5
                if move == 1:
                    #means there is an item in the right shelf of the target shelf
                    #thus the worker should go on unit longer to go inside these two shelves
                    start_address[0] = end_address[0]+0.5
                    distance = distance + 1
                
            else:
                start_address[0] = end_address[0]+0.5
                if move == -1:
                    #means there is an item in the right shelf of the target shelf
                    #thus the worker should go on unit longer to go inside these two shelves
                    start_address[0] = end_address[0]-0.5
                    distance = distance + 1
                
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)
            start_address[1] = end_address[1]
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)
            print("start address:%s"%start_address)
            print("end address:%s"%end_address)
            self.w.create_rectangle(start_address[0]*32+18,start_address[1]*32+18,start_address[0]*32+30,start_address[1]*32+30,fill='red')
            
        #After picking up all the item, the worker needs to go to his end location
        #Different from picking up item from right or left side of the shelf
        #   the end location could also be the up and down of a shelf
        end_address = [float(end[0]), float(end[1])]
        distance = distance + FindDistance(start_address,end_address)
        if (2*start_address[1])%2==1:
            if start_address[1] <= end_address[1]:
                start_address[1] = start_address[1] + 0.5
            else:
                start_address[1] = start_address[1] - 0.5
            
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)
        
        

        #Means the end location id on the up or down side of a shelf
        if (2*end_address[0])%2==1:
            if start_address[0] < end_address[0]:
                start_address[0] = end_address[0]-0.5
            else:
                start_address[0] = end_address[0]+0.5
            
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)

            start_address[1] = end_address[1]
            
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)
            
        else:
            start_address[0] = end_address[0]
            
            path.append(start_address[0]*32+24)
            path.append(start_address[1]*32+24)
        
        path.append(end_address[0]*32+24)
        path.append(end_address[1]*32+24)

        #print distance
        self.w.create_line(path, width = 8, fill = color)
        return distance

    #This function is used to show original path
    def ShowOrginPath(self):
        #print("algorithm: %d" %self.alg.get())
        raw_order = self.OrderEntry.get().split(",")
        order = []
        
        #eliminate the right and left side's space for each item
        for item in raw_order:
            order.append(item.strip())
        #print order
        start  = self.StartEntry.get().split(",")
        end = self.EndEntry.get().split(",")
        self.Refresh()
        self.MarkItem(order)
        
        #delete the content of cost entry before inserting
        self.CostEntry.delete(0, END)
        #insert the cost to the cost entry
        
        if self.weight.get() == 0:
            self.ShowPath(start, order, end, 'blue')
            self.CostEntry.insert(0,TotalCostWithWeight(start, order, end))
        elif self.weight.get() == 1:
            self.CostEntry.insert(0,self.ShowPath(start, order, end, 'blue'))
        
        #self.CostEntry.insert(0,self.ShowPath(start, order, end, 'blue'))
        return

    #This function is used to refresh the canvas
    def Refresh(self):
        self.w.delete('all')
        #draw the all the rectangles to represent the shelf
        self.shelf = []
        for i in range(20):
            self.shelf.append([])
            for j in range(11):
                self.shelf[i].append(self.w.create_rectangle(32*i+32,32*j+32,32*i+48,32*j+48, fill="yellow"))
                
    #This function is used to find an optimal order
    def FindOptimal(self):
        raw_order = self.OrderEntry.get().split(",")
        order = []
        
        #eliminate the right and left side's space for each item
        for item in raw_order:
            order.append(item.strip())
        start  = self.StartEntry.get().split(",")
        end = self.EndEntry.get().split(",")
        
        #insert the optimal order into the OptimalOrderEntry
        self.OptimalOrderEntry.delete(0, END)
        if self.alg.get() == 0:
            optimal_order = modified_NN(start, order, end)
        elif self.alg.get() == 1:
            optimal_order = branch_bound(start, order, end)
        print ("optimal order: %s" %optimal_order)
        
        self.OptimalOrderEntry.insert(END,optimal_order[0])
        for i in range(1,len(optimal_order)):
            self.OptimalOrderEntry.insert(END,","+optimal_order[i])
        #self.Refresh()
        #self.MarkItem(order)
        #delete the content of cost entry before inserting
        self.OptimalCostEntry.delete(0, END)
        #insert the cost to the cost entry
        if self.weight.get() == 0:
            self.ShowPath(start, optimal_order, end, 'green')
            self.OptimalCostEntry.insert(0,TotalCostWithWeight(start, optimal_order, end))
        elif self.weight.get() == 1:
            self.OptimalCostEntry.insert(0,self.ShowPath(start, optimal_order, end, 'green'))

    #This function is used to process the orders in file
    def ProcessFile(self):
        #open the input file and output file
        inputfile = self.InputFileEntry.get()
        outputfile = self.OutputFileEntry.get()
        fi = open(inputfile, "r")
        fo = open(outputfile, "w")
        
        start  = self.StartEntry.get().split(",")
        end = self.EndEntry.get().split(",")
        
        #store the result in the list
        self.optimal_orders = []
        self.lines = fi.readlines()
        if self.weight.get()==0:
            #means the user wants to consider about the weight
            capacity = float(self.WeightCapacity.get())
            self.orderweight = {}
            self.message=[]
            for line in self.lines:
                order = line.split()
                w = 0
                for item in order:
                    w = w + FindWeight(item)
                self.orderweight[line] = w
                self.message.append("Original")
            print self.lines[0]
            f = zip(self.orderweight.values(),self.orderweight.keys())
            print len(f)
            a = sorted(f)
            length = len(a)
            i = 0
            print length
            while i < length:
                #print "test"
                #merge the small orders
                if i+1 < length and a[i][0]+a[i+1][0]<capacity:
                    if len(a[i][1].split())+len(a[i+1][1].split())<20:
                        first_index = self.lines.index(a[i][1])
                        second_index = self.lines.index(a[i+1][1])
                        print self.lines[first_index]
                        print self.lines[second_index]
                        self.message[first_index]="Order is merged by "+ self.lines[first_index] +" and "+self.lines[second_index]
                        self.lines[first_index] = self.lines[first_index]+'\t'+self.lines[second_index]
                        self.message.pop(second_index)
                        self.lines.pop(second_index)
                        print("merge %d and %d" %(first_index,second_index))
                        i=i+1
                else:
                    print "break merge"
                    break
                i=i+1
                
                #split the large orders
                '''
                elif a[i][0]>=20:
                    first_index = self.lines.index(a[i][1])
                    order = a[i][1].split()
                    first_order = order[0:int(round(len(order)/2))]
                    second_order = order[int(round(len(order)/2)):len(order)]
                    temp_string = ''
                    for item in first_order:
                        temp_string=temp_string+item+"\t"
                    self.lines[first_index]=temp_string
                    self.message[first_index] = "Order is split by "+a[i][1]
                    temp_string = ''
                    w = 0
                    for item in second_order:
                        temp_string=temp_string+item+"\t"
                    self.lines.insert(first_index+1,temp_string)
                    self.message.insert(first_index+1,"Order is split by "+a[i][1])
                    print("split %d" %(first_index))
                i = i+1
                '''
            length = len(self.lines)
            i=0
            print "test"
            while i < length:
                temp_weight = self.orderweight.get(self.lines[i])
                print i
                if temp_weight==None:
                    #means this order is merged by other two orders before and
                    #does not to bee split
                    i=i+1
                    continue
                min_index=0
                if temp_weight>capacity:
                    #means the order is too big and needs to be split
                    temp_weight2 = 0
                    order = self.lines[i].split()
                    split_index = 0
                    line = self.lines[i]
                    #find out part of the order which is not big
                    print len(order)
                    print("temp weight:%s"%temp_weight)
                    for j in range(len(order)):
                        temp_weight2 = temp_weight2+FindWeight(order[j])
                        if temp_weight2 > capacity:
                            print("change split index: %d" %split_index)
                            split_index = j
                            temp_weight2 = temp_weight2-FindWeight(order[j])
                            break
                    print("temp weight2:%s"%temp_weight2)
                    print("split index: %d" %split_index)
                    if split_index==0:
                        print("item %s is out of capacity"%order[0])
                        temp_string = ''
                        for j in range(1,len(order)):
                            temp_string=temp_string+order[j]+"\t"
                        self.orderweight.pop(self.lines[i])
                        self.lines[i]=temp_string
                        
                        self.orderweight[self.lines[i]]=temp_weight-FindWeight(order[0])
                        continue
                    #insert the first half of the order, change the message
                    temp_string = ''
                    for j in range(split_index):
                        temp_string=temp_string+order[j]+"\t"
                    #if temp_string=='':
                    self.lines.insert(i, temp_string)
                    self.message[i]= self.message[i]+" Order is split by " + line
                    self.orderweight[temp_string]= temp_weight2
                    print("First split: %s"%temp_string)
                    print line
                    
                    #insert the second half of the order
                    temp_string = ''
                    for j in range(split_index,len(order)):
                        temp_string=temp_string+order[j]+"\t"
                    self.lines.insert(i+1, temp_string)
                    self.message.insert(i+1, " Order is split by " + self.lines[i+2])
                    self.orderweight[temp_string]=temp_weight-temp_weight2
                    print("Second split: %s"%temp_string)
                    print line
                        
                    #remove the original order, its weight
                    self.orderweight.pop(self.lines[i+2])
                    self.lines.pop(i+2)
                    length = length + 1
                i=i+1
            print "Finish Preprocessing"
    
        count = 0
        #go through the whole order
        for line in self.lines:
            count = count+1
            order = line.split()
            #print order
            #get the optimal order
            if self.alg.get() == 0:
                optimal_order = modified_NN(start, order, end)
            elif self.alg.get() == 1:
                optimal_order = branch_bound(start, order, end)
            
            #write the result to the corresponding outputfile
            for order in optimal_order:
                fo.write("%s "%(order))
            fo.write("\n\n")
            #add the result to the list
            self.optimal_orders.append(optimal_order)
            print count
    
        fo.write("\n\n")
        print "Finished"
        fi.close()
        fo.close()

    def PickOrder(self):
        start  = self.StartEntry.get().split(",")
        end = self.EndEntry.get().split(",")
        i = int(self.PickOrderEntry.get())
        if self.weight.get()==0:
            print self.message[i]
        order = self.lines[i].split()
        optimal_order = self.optimal_orders[i]
        
        self.OrderEntry.delete(0, END)
        self.OrderEntry.insert(END,order[0])
        for i in range(1,len(order)):
            self.OrderEntry.insert(END,","+order[i])
        
        self.OptimalOrderEntry.delete(0, END)
        self.OptimalOrderEntry.insert(END,optimal_order[0])
        for i in range(1,len(optimal_order)):
            self.OptimalOrderEntry.insert(END,","+optimal_order[i])

        self.Refresh()
        self.MarkItem(order)
        
        #delete the content of cost entry before inserting
        self.CostEntry.delete(0, END)
        #insert the cost to the cost entry
        if self.weight.get() == 0:
            self.ShowPath(start, order, end, 'blue')
            self.CostEntry.insert(0,TotalCostWithWeight(start, order, end))
        elif self.weight.get() == 1:
            self.CostEntry.insert(0,self.ShowPath(start, order, end, 'blue'))
        
        #delete the content of cost entry before inserting
        self.OptimalCostEntry.delete(0, END)
        #insert the cost to the cost entry
        if self.weight.get() == 0:
            self.ShowPath(start, optimal_order, end, 'green')
            self.OptimalCostEntry.insert(0,TotalCostWithWeight(start, optimal_order, end))
        elif self.weight.get() == 1:
            self.OptimalCostEntry.insert(0,self.ShowPath(start, optimal_order, end, 'green'))
        return



#build the root of the GUI
root = Tk()
gui = GUIforPickOrder(root)
#run the GUI until it gets closed
root.mainloop()

