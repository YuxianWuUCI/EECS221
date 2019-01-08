#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy

frw = open("item-dimensions-tabbed.txt", "r")
linesw = frw.readlines()
frw.close()

fr = open("warehouse-grid.csv", "r")
lines = fr.readlines()
fr.close()

def FindItem( target_id ):
    target_address = []
    for line in lines:
        item = line.split(',')
        if target_id == item[0]:
            target_address = [round(float(item[1]))+0.5, round(float(item[2]))+0.5]
    if len(target_address) == 0:
        print ("Error: Target %s not found"%target_id)
    return target_address

def is_item(address):
    if (2*float(address[0]))%2 == 1 and (2*float(address[1]))%2 == 1:
        return True
    return False

def FindDistance(start_address, end_address):
    distance = abs(float(end_address[0])-float(start_address[0]))+abs(float(end_address[1])-float(start_address[1]))
    if is_item(end_address):
        distance = distance - 0.5
    
    #Means the start address is on the same horizontal line of the target address
    #but having shelf within the straight line
    if start_address[1] == end_address[1] and abs(start_address[0]-end_address[0])>0.5:
        distance = distance + 1
    
    #Means the start address is on the up or the down side of the target address
    elif start_address[0] == end_address[0] and abs(start_address[1]-end_address[1])==0.5:
        distance = distance + 1
    
    return distance

'''
    each line includes these information:
    Item id, length (inches), width (inches), height (inches), weight (lbs)
    
    Now the algorithm only needs to consider about the weight
    
    defines a function that can find weight of each item based on the item id
'''
#This function returns the weight of the item
#Input:     item id, String
#Output:    weight, Float
def FindWeight(target_id):
    weight = 0.0
    for line in linesw:
        line = line.split()
        if line[0] == target_id:
            weight = float(line[4])
            #print("%s: %f" %(target_id,weight))
            return weight
    #print("%s: %f" %(target_id,weight))
    return weight

#This function returns the effort worker costs for finishing this order
#Input: start address, [float, float]
#       orders, [item id, ...]
#       end address, [float, float]
#Output:effort, float
def TotalCostWithWeight(start, orders, end):
    start_address = copy.copy(start)
    effort = 0
    weight = 0
    for i in range(len(orders)):
        end_address = FindItem(orders[i])
        if len(end_address) == 0:
            print ('Error: Item %s does not have an address' %orders[i])
            continue
    #print("Worker goes from %s with weight %5.2f to pick up item %s in %s whose weight is %5.2f"%(start_address, weight,orders[i], end_address, FindWeight(orders[i])))
        effort = effort + weight*FindDistance(start_address,end_address)
        #   print("This costs %5.2f effort"%(weight*FindDistance(start_address,end_address)))
        weight = weight + FindWeight(orders[i])
        if float(start_address[0]) < float(end_address[0]):
            start_address[0] = float(end_address[0])-0.5
        else:
            start_address[0] = float(end_address[0])+0.5
        start_address[1] = end_address[1]

#print("Worker goes from %s with weight %5.2f to the end address in %s"%(start_address, weight, end))
    #print("This costs %5.2f effort"%(weight*FindDistance(start_address,end)))
    effort = effort + weight*FindDistance(start_address,end)
    #print("Total Effort: %5.2f\n\n"%effort)
    return effort

def ReadOrderWithWeight():
    fv = open("warehouse-orders-v02-tabbed.txt", "r")
    linesw = fv.readlines()
    fv.close()
    for i in range(3):
        print TotalCostWithWeight(start, linesw[i].split(), end)
    return

#This function write the whole details of path into the requested file
def DisplayPathWithWeight(start, orders, end, fo):
    #transfer the string adrress "start" into float address "start_address"
    start_address = [float(start[0]), float(start[1])]
    effort = 0
    weight = 0
    for order in orders:
        end_address = FindItem(order)
        if len(end_address) == 0:
            print ('Error: Item %s does not have an address' %orders[i])
            continue
        fo.write("Worker goes from %s with weight %5.2f to pick up item %s in %s whose weight is %5.2f"%(start_address, weight,order, end_address, FindWeight(order)))
                 
        effort = effort + weight*FindDistance(start_address,end_address)
        fo.write("This costs %5.2f effort"%(weight*FindDistance(start_address,end_address)))
        weight = weight + FindWeight(order)
        if float(start_address[0]) < float(end_address[0]):
            start_address[0] = float(end_address[0])-0.5
        else:
            start_address[0] = float(end_address[0])+0.5
        start_address[1] = end_address[1]
    #After picking up all the items, worker now needs to go to the destination
    fo.write("Worker goes from %s with weight %5.2f to the end address in %s"%(start_address, weight, end))
    fo.write("This costs %5.2f effort"%(weight*FindDistance(start_address,end)))
    effort = effort + weight*FindDistance(start_address,end)
    fo.write("Total Effort: %5.2f\n\n"%effort)

'''
start = [0,0]
end = [0,0]
ordres = ['33139', '33211', '34068']
fv = open("warehouse-orders-v02-tabbed.txt", "r")
linesv = fv.readlines()
fv.close()
for i in range(3):
    print TotalCostWithWeight(start, linesv[i].split(), end)
'''



