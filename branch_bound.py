#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import numpy library for matrix calculation
from numpy import *
import numpy as np
import copy
from project5 import FindItem


INFINITY=999

'''
fr = open("warehouse-grid.csv", "r")
global lines
lines = fr.readlines()
fr.close()
#Find the address of a specific item
#Input: the ID of the item, string
#Output: address of the item, list(length is 2, both type are float)
def FindItem( target_id ):
    #print("%s seconds spent for reading the \"warehouse-grid.csv\" file " %(str(t1-t0)))
    target_address = []
    for line in lines:
        comma_pos = line.find(',');
        if target_id == line[0:comma_pos]:
            #这里用+2来跳过逗号后面的空格
            #将字符型先转成浮点数，再用四舍五入转为整型（虽然round返回的还是浮点数）
            target_address.append(round(float(line[comma_pos+2:line.find(',',comma_pos+1)]))+0.5)
            comma_pos = line.find(',',comma_pos+1)
            target_address.append(round(float(line[comma_pos+2:]))+0.5)
            #print "目标item的地址：", target_address
            break
    if len(target_address) == 0:
        print "target not found"
    return target_address
'''

def divide_order(order):
    i = 0
    count = len(order)
    while i<count:
        if order[i].find(",")!=-1:
            suborder = order[i].split(",")
            order.remove(order[i])
            count = count - 1
            for j in range(len(suborder)):
                order.insert(i,suborder[j].strip())
                i = i+1
                count = count + 1
        else:
            i = i+1
    return order

'''
    This funtion use the branch and bound algorithm to a relatively good path
    which starts from star address, pick up all the items in order and finally end in end address
    input: star (start address, 2 float list), order(list of items' ID, string), end (end address, 2 float list)
    output: branch_bound_order (the order of picking up items in order, list of items' ID, string)
'''
def branch_bound(start_address, order, end_address):
    start = [float(start_address[0]), float(start_address[1])]
    end = [float(end_address[0]), float(end_address[1])]
    branch_bound_order = []
    lowest_cost = INFINITY
    cost = 0
    count = 0
    #create a list to store all the addresses needed to calculate the distance
    #lenght of the list would be 2*len(order)+1 since it includes the start address and two sides of each item
    temp_address = []
    #print("start address: %s" %(start))
    for i in range(len(order)):
        item_address = FindItem(order[i])
        temp_address.append(item_address)
        '''
        #add the left side of ith item
        address.append([item_address[0]-0.5, item_address[1]])
        #add the right side of ith item
        address.append([item_address[0]+0.5, item_address[1]])
        '''
    count = len(order)
    it = 0

    #merge the item which has the same address
    while it<count:
        if temp_address.count(temp_address[it])!=0:
            #means there are some items have same address as this item
            next = it+1
            for i in range(temp_address.count(temp_address[it])-1):
                next = temp_address.index(temp_address[it],next)
                temp_address.pop(next)
                order[it]=order[it]+', '+order[next]
                order.pop(next)
                count = count-1
        it = it + 1

    #create a list to store all the addresses needed to calculate the distance
    #lenght of the list would be 2*len(order)+1 since it includes the start address and two sides of each item
    count = 0
    address = [start]
    for i in range(len(order)):
        address.append([temp_address[i][0]-0.5, temp_address[i][1]])
        address.append([temp_address[i][0]+0.5, temp_address[i][1]])
    
    #build the first reduce matrix
    #    print("\n\naddress:\n%s\n\n" %address)
    reduce_matrix = mat(zeros((len(address),len(address))))
    for i in range(len(address)):
        for j in range(len(address)):
            #calculate the distance between each address
            if i == j:
                reduce_matrix[i,j] = INFINITY
            if reduce_matrix[i,j] == 0:
                reduce_matrix[i,j] = abs(address[j][0]-address[i][0])+abs(address[j][1]-address[i][1])
                reduce_matrix[j,i]=reduce_matrix[i,j]
#print("reduce matrix:\n%s\n\n" %reduce_matrix)

    reduce = copy.copy(reduce_matrix)
    #find the min of each row and add them to the cost
    cost = cost + np.min(reduce,1).sum()
    reduce = reduce - np.min(reduce,1)
    reduce[np.where(reduce>(INFINITY-100))] = INFINITY
    #find the min of each column
    cost = cost + np.min(reduce,0).sum()
    reduce = reduce - np.min(reduce,0)
    reduce[np.where(reduce>(INFINITY-100))] = INFINITY
    #print("after reduce:\n%s\n\n" %reduce)
    #print("cost:%s\n\n" %cost)
    stack_order=[]
    
    
    
    '''
        for each node in branch and bound tree
        0 is the order this node stands for
        1 is the index of address worker currently stay
        2 is the reduce_matrix it has
        3 is the current lower bound it has
    '''
    
    #first, calculate the evaluation lower bound for picking up different first item
    for i in range(len(order)):
        temp_cost = cost
        stack_item = []
        temp_reduce = copy.copy(reduce)
        #store the order which this branch represents
        stack_item.append([order[i]])
        
        #store the location after pick up the ith item
        if reduce_matrix[0, 2*i+1] < reduce_matrix[0, 2*i+2]:
            #if left side of ith item is closer to the star address
            stack_item.append(2*i+1)
            temp_cost = temp_cost + reduce_matrix[0, 2*i+1]
        else:
            temp_cost = temp_cost + reduce_matrix[0, 2*i+2]
            stack_item.append(2*i+2)
        
        #renew the reduce matrix
        for j in range(len(address)):
            temp_reduce[0,j]=INFINITY
            temp_reduce[j,2*i+1]=INFINITY
            temp_reduce[j,2*i+2]=INFINITY
            temp_reduce[j,0]=INFINITY

        temp_cost = temp_cost + (np.min(temp_reduce,1)%INFINITY).sum()
        temp_reduce = temp_reduce - (np.min(temp_reduce,1)%INFINITY)
        temp_reduce[np.where(temp_reduce>(INFINITY-100))] = INFINITY

        temp_cost = temp_cost + (np.min(temp_reduce,0)%INFINITY).sum()
        temp_reduce = temp_reduce - (np.min(temp_reduce,0)%INFINITY)
        temp_reduce[np.where(temp_reduce>(INFINITY-100))] = INFINITY

        #store the new reduce matrix in the stack
        stack_item.append(temp_reduce)
        #store the lower bound of this node
        temp_cost = temp_cost + (abs(end[0]-address[stack_item[1]][0])+abs(end[1]-address[stack_item[1]][1]))
        stack_item.append(temp_cost)

#print("order: %s\nlocation: %s\ncost: %s\n\n\n " %(stack_item[0], stack_item[1], stack_item[3]))
        stack_order.append(stack_item)
                       
    next_node = -1
    #then, calculate the lower bound for the next item
    while len(stack_order) != 0 and count<5000:
        count = count+1
        min_item = 0
        min_cost = stack_order[0][3]
        max_level = 1
        #find the next node for the expansion
        if next_node < 0:
            for i in range(len(stack_order)):
                #if this node has a lower lower bound or has the same lower bound but with a deeper layer
                #change the best node so far
                if stack_order[i][3] < min_cost:
                    min_item = i
                    min_cost = stack_order[i][3]
                    max_level=len(stack_order[i][0])
                elif stack_order[i][3] == min_cost and len(stack_order[i][0])>max_level:
                    min_item = i
                    min_cost = stack_order[i][3]
                    max_level=len(stack_order[i][0])
    
        #print("stack_order[min_item]: %s" %stack_order[min_item])
            current_node = stack_order[min_item]
            stack_order.pop(min_item)
        else:
            #print"next node: ", next_node
            current_node = stack_order[next_node]
            stack_order.pop(next_node)
#print("current order: %s\nlocation: %s\n cost: %s\n " %(current_node[0], current_node[1], current_node[3]))
        if current_node[3] >= lowest_cost:
            #if the lowerbound in this node costs bigger than the best found tour so far
            #we should prune this branch
            if next_node<0:
                
                print("branch bound order: %s\n\n"%branch_bound_order)
                return divide_order(branch_bound_order)
            else:
                next_node=-1
                #print("prune!!!!!!!!!")
                continue


        current_location = current_node[1]
        if len(current_node[0]) == len(order):
            #means the current node is a leaf node
            #then we should compare it with the best found tour so far
            #first, compute the cost of this new found tour
            #print("leaf node!!!!")
            #print"leaf node: ",current_node[0]
            temp_cost = current_node[3]
            next_node = -1
            if temp_cost<lowest_cost:
                lowest_cost = temp_cost
                branch_bound_order = current_node[0]
#print("lowest cost: %s !!!\n\n"%lowest_cost)
        else:
            least_son = INFINITY
            for i in range(len(order)):
                
                temp_reduce = copy.copy(current_node[2])
                if temp_reduce[current_location, 2*i+1] != INFINITY:
                    #which means worker has not picked up this item
                    temp_order = copy.copy(current_node[0])
                    stack_item=[]
                    
                    temp_cost = current_node[3] - (abs(end[0]-address[current_location][0])+abs(end[1]-address[current_location][1]))
                    #print("append order: %s" %order[i])
                    #print("current node[0]: %s" %current_node[0])
                    temp_order.append(order[i])
                    #print("temp order: %s" %temp_order)
                    stack_item.append(temp_order)
                    if reduce_matrix[current_location, 2*i+1] < reduce_matrix[current_location, 2*i+2]:
                        #if left side of ith item is closer to the star address
                        stack_item.append(2*i+1)
                        temp_cost = temp_cost + reduce_matrix[current_location, 2*i+1]
                    else:
                        temp_cost = temp_cost + reduce_matrix[current_location, 2*i+2]
                        stack_item.append(2*i+2)
                    for j in range(len(address)):
                        temp_reduce[current_location,j]=INFINITY
                        if current_location%2 == 1:
                            temp_reduce[current_location+1,j]=INFINITY
                        else:
                            temp_reduce[current_location-1,j]=INFINITY
                        temp_reduce[j,2*i+1]=INFINITY
                        temp_reduce[j,2*i+2]=INFINITY
                #print("temp reduce1: %s" %temp_reduce)
                #print("np min row: %s" %(np.min(temp_reduce,1)%INFINITY))
                    temp_cost = temp_cost + (np.min(temp_reduce,1)%INFINITY).sum()
                    temp_reduce = temp_reduce - np.min(temp_reduce,1)%INFINITY
                    temp_reduce[np.where(temp_reduce>(INFINITY-100))] = INFINITY
                    #print("temp reduce2: %s" %temp_reduce)
                    #print("np min col: %s" %(np.min(temp_reduce,0)%INFINITY))
                    temp_cost = temp_cost + (np.min(temp_reduce,0)%INFINITY).sum()
                    temp_reduce = temp_reduce - (np.min(temp_reduce,0))%INFINITY
                    #print("temp reduce3: %s" %temp_reduce)
                    temp_reduce[np.where(temp_reduce>(INFINITY-100))] = INFINITY
                    #store the new reduce matrix in the stack
                    stack_item.append(temp_reduce)
                    #store the lower bound of this node
                    temp_cost = temp_cost + (abs(end[0]-address[stack_item[1]][0])+abs(end[1]-address[stack_item[1]][1]))
                    stack_item.append(temp_cost)
                    stack_order.append(stack_item)
                    if least_son > temp_cost:
                        next_node = len(stack_order) - 1
                        least_son = temp_cost
                    
                    #print("added node order: %s\nlocation: %s\ncost: %s\n " %(stack_item[0], stack_item[1], stack_item[3]))
                    #print"stack size", len(stack_order)
                    #print"\n\n"
                        
                        
    print("counta: %s" %count)
    print("branch bound order: %s"%branch_bound_order)
    return divide_order(branch_bound_order)

'''
start = [0,0]
end = [18,0]
order = ["281610", "342706", "111873", "198029", "366109", "287261",    "76283", "254489", "258540", "286457"]
print branch_bound(copy.copy(start), order, copy.copy(end))
'''
