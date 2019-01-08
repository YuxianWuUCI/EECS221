#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import copy

#This is the modified version of nearest neighbour algorithm
#In this version, the algorithm will choose several different address
#as start address, including original start address and each item's address,
#calculate a circle path for each start address and insert the end address appropriately
#
#Then it will find the shortest one among these paths
#
#note: since it is complicated to pick the side of item if not start from the original
#start address, I decide to use the items' own address in finding the nearest neighbour
#and calculate the total cost in traditional way
def modified_NN(start, original_order, end):
    #first, calculate the traditional NN path which start from start address
    temp_order = copy.copy(original_order)
    start_address = copy.copy(start)
    temp_optimal = []
    while len(temp_order) != 0:
        min_distance = 65535
        min_index = -1
        
        
        #calculate the distance between start address and each item
        #then find the nearest item
        for i in range(len(temp_order)):
            end_address = FindItem(temp_order[i])
            distance = abs(float(end_address[0])-float(start_address[0]))+abs(float(end_address[1])-float(start_address[1]))
            if distance < min_distance:
                min_distance = distance
                min_index = i
        #means the algorithm works wrongly
        if min_index == -1:
            print("wrong in finding the nearest neighbour in the %d iteration" %(len(original_order)-len(temp_order)))
            return
                
                
        #set the next start address as the right or left side of the item worker picked up
        end_address = FindItem(temp_order[min_index])
        #add this item to the optimal order and delete it from the original order
        #so that it will not be considered next time
        temp_optimal.append(temp_order[min_index])
        temp_order.remove(temp_order[min_index])
        if start_address[0] < end_address[0]:
            start_address[0] = end_address[0]-0.5
        else:
            start_address[0] = end_address[0]+0.5
        start_address = end_address[1]


    #calculate the cost of the traditional NN path
    temp_cost = TotalCost(start, temp_optimal, end)
    min_cost = temp_cost
    optimized_order = temp_optimal
    for order in original_order:
        #choose each order as the start address
        temp_order = copy.copy(original_order)
        start_address = FindItem(order)
        temp_optimal = [order]
        temp_order.remove(order)
        #document whether the start has been added to the temp_optimal
        include_start = False
        while len(temp_order) != 0 or not include_start:
            if not include_start:
                min_distance = abs(float(start[0])-float(start_address[0]))+abs(float(start[1])-float(start_address[1]))
            else:
                min_distance = 65535
            min_index=-1
            
            for i in range(len(temp_order)):
                end_address = FindItem(temp_order[i])
                distance = abs(float(end_address[0])-float(start_address[0]))+abs(float(end_address[1])-float(start_address[1]))
                if distance < min_distance:
                    min_distance = distance
                    min_index = i
            
            if min_index>-1:
                #add the nearest item as usual
                temp_optimal.append(temp_order[min_index])
                end_address = FindItem(temp_order[min_index])
                temp_order.remove(temp_order[min_index])
                if start_address[0] < end_address[0]:
                    start_address[0] = end_address[0]-0.5
                else:
                    start_address[0] = end_address[0]+0.5
                start_address[1] = end_address[1]
            elif not include_start:
                #this means start is the nearest neighbour
                temp_optimal.append(start)
                include_start = True
                start_address = copy.copy(start)
            else:
                #means algorithm can not find a nearest neighbour
                print("mistake for finding the nearest neighbour in the %d iteration" %(len(original_order)-len(temp_order)+1))
                return
        temp_optimal.extend(temp_optimal)
        min_index = temp_optimal.index(start)
        #make the order of this path correctly
        temp_optimal = temp_optimal[min_index+1:min_index+len(original_order)+1]
        
        temp_cost = TotalCost(start, temp_optimal, end)
        
        #if this path is better than the best path so far
        if temp_cost<min_cost:
            min_cost = temp_cost
            optimized_order=temp_optimal
                
                
    return optimized_order













