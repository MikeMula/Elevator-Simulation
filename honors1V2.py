

import random
import numpy
import pylab


def generate_passengers():
    '''Generate passenger data for one simulation run.
       List items are a tuple: (arrival_time, source_floor, destination_floor)
       Return: List, elevator speed (sec/floor), loading/unloading rate (sec/pass)
       Implicitly uses the simulation's seed for random.randint.
    '''
    FLOORS = 20       # number of floors: 20
    PASSENGERS = 1000 # number of passengers: 1000
    ELEVATOR_SPEEDS = [0.5, 1, 1.5, 2] # possible speeds of elevator (sec/floor)
    LOADING_RATE = [0.2, 0.3, 0.4] # possible speed of passenger to load and unload    
   
    t = 0
    L = []
    random.shuffle(ELEVATOR_SPEEDS)
    random.shuffle(LOADING_RATE)
    for i in range(PASSENGERS):
        t += numpy.random.poisson()
        L.append((t, random.randint(0, FLOORS), random.randint(0, FLOORS)))
    return L,ELEVATOR_SPEEDS[0],LOADING_RATE[0]

def load_passengers(passenger_list, onboard_list, current_time, current_floor, \
                    loading_rate, capacity, fp):
    '''Load passengers up to capacity, update the time and return the the list
    of passenegers onboard, the passengers_list, the elevator position and the
    updated time'''
    
    c_pas = 0 #count of passengers loading
    my_list = passenger_list[:]
    for passenger in my_list:
        src_floor = passenger[1]
        arrival_time = passenger[0]
        
        if len(onboard_list) < capacity:
            #arrival time is now or earlier
            if (src_floor == current_floor) and (arrival_time <= current_time): 
                
                     #remove passenger dealt with from file(main list)
                    p = passenger_list.pop(passenger_list.index(passenger)) 
                    onboard_list.append(p)     #load the passenger
                    c_pas += 1
                         
    time_b4_loading = current_time
       
    print(file=fp)
    print("{:^16d}{:<12.2f}".format(current_floor, time_b4_loading), end='', file=fp)
      
    time_taken = c_pas * loading_rate
       
    current_time += time_taken #update current time
  
    print("{:<9.2f}{:^12d}".format(time_taken, len(onboard_list)), end= '', file = fp)       
    print("{:^16.2f}".format(current_time), end='', file=fp)
    
    return onboard_list, current_time, current_floor, passenger_list, time_b4_loading

def move_passengers(passenger_list, onboard_list, elevator_speed, current_time, current_floor, fp):
    ''' Move passengers and return the updated time, elevator position and passengers
    still onboard'''
     
    waiting_list = [] #floors with people waiting at current time
    for passenger in passenger_list:
        if passenger[0] <= current_time: 
                waiting_list.append(passenger[1])
    
    if len (onboard_list) != 0: #there are passengers onboard
    
        rand_passenger = random.choice(onboard_list) # pick a random passenger
        rand_dst_floor = rand_passenger[2]
               
        floors_moved = abs (rand_dst_floor - current_floor)
        move_time = floors_moved * elevator_speed
        
        print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor, rand_dst_floor, \
               move_time), end='', file = fp)
        
        #update the time and position of elevator
        current_time += move_time     
        current_floor = rand_dst_floor 
    
        print("{:>14.2f}".format(current_time),end='', file = fp)
          
        return onboard_list, current_time, current_floor
    
    elif len(onboard_list) == 0 and len(waiting_list) != 0: #no more passengers onboard 

        rand_dst_floor = random.choice(waiting_list) #random floor from waiting list
    
        #move to the randomly selected floor
        floors_moved = abs (rand_dst_floor - current_floor)
        move_time = floors_moved * elevator_speed
        
        print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor, rand_dst_floor,\
               move_time), end='', file = fp)
        
        #update the time and position of elevator
        current_time += move_time     
        current_floor = rand_dst_floor
        
        print("{:>14.2f}".format(current_time),end='', file = fp)
        
        return onboard_list, current_time, current_floor
     
    elif (len(waiting_list)== 0) and (len(onboard_list)== 0):  
        
        #list of people to potentially be loaded after letting time pass
        potential_trans_list = [] 
        
        while len(passenger_list) != 0: #still passengers on file
            
            current_time += 1   #let time pass
            
            for passenger in passenger_list:
                if passenger[0] <= current_time:
                    potential_trans_list.append(passenger)
                    
            if len (potential_trans_list ) == 0:
                continue                        #if still no one, let more time pass
                
            else:
                potentials = []  # people waiting on other floors at current time
                
                for person in potential_trans_list:
                    if person[1] == current_floor:  #at least one person on current floor
                        
                        return onboard_list, current_time, current_floor
                        
                    else:
                        potentials.append(person)
                
                #only gets here if no one is waiting on current floor at current time
                
                #select a random person from potentials, go pick them up
                rand_person = random.choice(potentials)
                floors_moved = abs (rand_person[1] - current_floor)
                move_time = floors_moved * elevator_speed              
                
                print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor,\
                       rand_person[2], move_time), end='', file = fp)
                
                #update the time and position of elevator
                current_time += move_time     
                current_floor = rand_person[1]  
            
                print("{:>14.2f}".format(current_time),end='', file = fp)
                
                return onboard_list, current_time,  current_floor
                                    
def unload_passengers(onboard_list, loading_rate, current_time, current_floor,\
                      wait_time_list, time_b4_loading,fp):
    '''Unload passengers and return updated time, elevator position, list on
    board, and a wait_tme_list'''
    
    c_unload = 0 #count of people getting off
    exit_list = []

    my_list = onboard_list[:]
    for passenger in my_list:
        if passenger[2] == current_floor:
            #unload all passengers with this destination
            exit_list.append(onboard_list.pop(onboard_list.index(passenger))) 
            c_unload += 1
            
    time_taken =  c_unload * loading_rate #time to unload
    current_time += time_taken
    
    for passenger in exit_list:
        wait_time = round ((current_time - passenger[1]),4)
        wait_time_list.append(wait_time)
    
    time_after_exit = current_time 
    tot_time4_movement = (time_after_exit) - (time_b4_loading)
    
    print("{:>11d}{:>10.2f}{:>15.2f}".format(c_unload, time_taken, \
          current_time),end='', file = fp)  
    print("{:>16.2f}".format(tot_time4_movement),file = fp, end='')
  
    return onboard_list, current_time, current_floor, wait_time_list
    

def Random_Elevator(capacity, fp):
    '''Calls appropriate functions to run random elevator simulation '''
    
    print(file=fp)
    onboard_list = []
    wait_time_list = []
    current_time = 0
    current_floor = 0

    passenger_list, elevator_speed, loading_rate = generate_passengers()
    
    print("--"*10, "BEGINNING OF RANDOM ELEVATOR SIMULATION", "--"*10,file = fp)
    #OUTPUT FORMATTING 
    print(file=fp)
    print("{:<16s}{:<12s}".format("current floor|","t b4 load|" ), end='', file=fp)
    print("{:<9s}{:<12s}".format("load t|", "p onboard|"), end= '',file=fp) 
    print("{:<16s}".format("t after load|"),end='', file=fp)
    print("{:<12s}{:<12s}{:<9s}".format("src floor|", "dst floor|", "move t|" )\
          , end='', file=fp)
    print("{:<15s}".format("t after move|"), end='', file=fp)
    print("{:<12s}{:<11s}{:<16s}".format("p exiting|", "unload t|", \
          "t after exit|"), end='', file=fp)
    print("{:<17s}".format("total t for move|"), file=fp)
    print(file = fp)
    print(file = fp)
       
    elevator_moves = 0
    while len(passenger_list) != 0:
    
        onboard_list, current_time, current_floor, passenger_list, \
        time_b4_loading = load_passengers(passenger_list, onboard_list, \
                                          current_time, current_floor, \
                                          loading_rate, capacity,fp)
        
        onboard_list, current_time, current_floor = move_passengers(passenger_list,\
        onboard_list, elevator_speed, current_time, current_floor,fp)
        elevator_moves += 1
        
        onboard_list, current_time, current_floor, wait_time_list = \
        unload_passengers(onboard_list, loading_rate, current_time, \
                          current_floor, wait_time_list, time_b4_loading,fp)
    
    print(file = fp)
    print(file = fp)
    print("Total time to deliver all passengers: {:.4f} seconds".\
          format(current_time),file = fp)
    print("Total Number of elevator movements: ", elevator_moves,file = fp)
    
    print(file = fp)
    print("--"*10, "END OF RANDOM ELEVATOR SIMULATION", "--"*10,file = fp)
    
    return current_time, elevator_moves,wait_time_list

####################STRATEGY ELEVATOR FUNCTIONS BEGIN HERE####################

def load_passengers2(passenger_list, onboard_list, current_time, current_floor,\
                     loading_rate, capacity, fp):
    '''Load passengers up to capacity, update the time and return the list 
    of passenegers onboard, updated time, elevator position and the time before
    loading'''
    
    c_pas = 0 #count of passengers loading
    my_list = passenger_list[:]
    for passenger in my_list:
        src_floor = passenger[1]
        arrival_time = passenger[0]
        
        if len(onboard_list) < capacity:
            #arrival time is now or earlier
            if (src_floor == current_floor) and (arrival_time <= current_time): 
                    #remove passenger dealt with from file(main list)
                    p = passenger_list.pop(passenger_list.index(passenger)) 
                    onboard_list.append(p)     #load the passenger
                    c_pas += 1
                         
    time_b4_loading = current_time
    
    print("{:^16d}{:<12.2f}".format(current_floor, current_time), end='', file=fp)
              
    time_taken = c_pas * loading_rate
    current_time += time_taken #update current time
    
    print("{:<9.2f}{:^12d}".format(time_taken, len(onboard_list)), end= '', file = fp) 
    print("{:^16.2f}".format(current_time), end='', file=fp)

    return onboard_list, current_time, current_floor, passenger_list, time_b4_loading

def move_passengers2(passenger_list, onboard_list, elevator_speed, current_time,\
                     current_floor, fp):
    ''' Move passengers and return the updated time, elevator position and the
    list of people onboard'''
      
    waiting_list = [] #floors with people waiting at current time
    waiting_dict = {}
    
    for passenger in passenger_list:
        if passenger[0] <= current_time: 
                waiting_list.append(passenger)
    
    if len (onboard_list) != 0: #there are passengers onboard

        destinations = []
        distances = []
        closest_passengers = []
        
        for passenger in onboard_list:
            dst_floor = passenger[2]
            #destination relative to current floor
            distance = abs(dst_floor - current_floor)  
            distances.append(distance)
            
            passenger_tup = passenger, distance
            destinations.append(passenger_tup)
        
        for persons in destinations:
            if persons[1] == min (distances):
                closest_passengers.append(persons[0])   
                
        if len (closest_passengers)!= 1: #there's more than one
            
            rand_person = random.choice(closest_passengers)
            dst_floor_go = rand_person[2]
            
        else:
            for person in closest_passengers:
                dst_floor_go = person[2]
                
        #move to selected floor       
        floors_moved = abs (dst_floor_go - current_floor)
        move_time = floors_moved * elevator_speed
            
        print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor, dst_floor_go, \
               move_time), end='', file = fp)
        
        #update the time and position of elevator
        current_time += move_time     
        current_floor = dst_floor_go 
    
        print("{:>14.2f}".format(current_time),end='', file = fp)
        
        return onboard_list, current_time, current_floor
    
        
    elif len(onboard_list) == 0 and len(waiting_list) != 0: #no more passengers onboard
        
        list_with_most = [] #floors with most people waiting
        
        for waiter in waiting_list:
            source_floor = waiter[1]
            
            if source_floor in waiting_dict:
                waiting_dict[source_floor] += 1
            else:
                waiting_dict[source_floor] = 1
        #floor with the most people waiting
        most_floor = max ([value for key,value in waiting_dict.items()]) 
        
        for key,value in waiting_dict.items():
            
            if value == most_floor:
                list_with_most.append(key)
        
        rel_distances = []  #relative distances
        closest_floors = []
        floors_with_most = []  #tuples of floor with their relative distances
        
        if len(list_with_most) != 1:
            
            for src_floor in list_with_most:
                distance = abs(src_floor - current_floor)
                rel_distances.append(distance)
                floors_with_most.append((src_floor, distance))       
            
            for flor in floors_with_most:
                if flor[1] == min (rel_distances):
                    closest_floors.append(flor[0])
                    
            if len(closest_floors) != 1: #if more than one floor is 'closest'
                
                dst_floor  = closest_floors[0] #choose arbitrarily 
            
            else:
                for elem in closest_floors:
                    dst_floor = elem
                
        else:
            for floor in list_with_most:
                dst_floor = floor 
                    
        #move to the  selected floor
        floors_moved = abs (dst_floor - current_floor)
        move_time = floors_moved * elevator_speed
        
        print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor, dst_floor, \
               move_time), end='', file = fp)
        
        #update the time and position of elevator
        current_time += move_time     
        current_floor = dst_floor
        
        print("{:>14.2f}".format(current_time),end='', file = fp)
        
        return onboard_list, current_time, current_floor
    
     
    elif (len(waiting_list)== 0) and (len(onboard_list)== 0):  
        
        potential_trans_list = [] #list of people to potentially be loaded after letting time pass
        
        while len(passenger_list) != 0:
            
            current_time += 1   #let time pass
            
            for passenger in passenger_list:
                if passenger[0] <= current_time:
                    potential_trans_list.append(passenger)
                    
            if len (potential_trans_list ) == 0:
                continue                        #if still no one, let more time pass
                
            else:
                potentials = []  # people waiting on other floors at current time
                
                for person in potential_trans_list:
                    if person[1] == current_floor:  #at least one person on current floor
                        
                        return onboard_list, current_time, current_floor   
                        
                    else:
                        potentials.append(person)
                
                #only gets here if no one is waiting on current floor at current time
                
                #select closest person from potentials, go pick them up
                closest_potentials = [] 
                closest_flors = []
                relative_distances = []
                for member in potentials:
                    
                    sc_floor = member[1]
                    distance_rel = abs (sc_floor - current_floor)
                    relative_distances.append(distance_rel)
                    closest_flors.append((sc_floor, distance_rel))
                    
                for flors in closest_flors:
                    if flors[1] == min (relative_distances):
                        closest_potentials.append(flors[0])
                        
                if len(closest_potentials) != 1: #more than one closest
                    
                    dst_floor = closest_potentials[0] #select arbitrarily
                
                else:
                    for element in closest_potentials:
                        dst_floor = element    
                               
                floors_moved = abs (dst_floor - current_floor)
                move_time = floors_moved * elevator_speed             
                
                print ("{:^11d}{:^11d}{:^8.2f}".format(current_floor, dst_floor,\
                       move_time), end='', file = fp)
                
                #update the time and position of elevator
                current_time += move_time     
                current_floor = dst_floor  
            
                print("{:>14.2f}".format(current_time),end='', file = fp)
                
                return onboard_list, current_time,  current_floor
                  
                    
def unload_passengers2(onboard_list, loading_rate, current_time, current_floor,\
                       wait_time_list, time_b4_loading, fp):
    '''Unload passengers and return updated time, elevator position, and list
    on board and waiting_time_list'''
    
    c_unload = 0 #count of people getting off
    exit_list = []

    my_list = onboard_list[:]
    for passenger in my_list:
        if passenger[2] == current_floor:
            #unload all passengers with this destination
            exit_list.append(onboard_list.pop(onboard_list.index(passenger)))  
            c_unload += 1
            
    time_taken =  c_unload * loading_rate #time to unload
    current_time += time_taken
    
    for passenger in exit_list:
        wait_time = round ((current_time - passenger[1]),4)
        wait_time_list.append(wait_time)
    
    
    time_after_exit = current_time 
    tot_time4_movement = (time_after_exit) - (time_b4_loading)
    
    print("{:>11d}{:>10.2f}{:>15.2f}".format(c_unload, time_taken, \
          current_time),end='', file = fp) 
    print("{:>16.2f}".format(tot_time4_movement),file = fp, end='')
    print(file=fp)
    
    return onboard_list, current_time, current_floor, wait_time_list
    

def Strategy_Elevator(capacity, fp):
    ''' Call appropriate functions to run strategy elevator simulation '''
    
    print(file = fp) 
    
    onboard_list = []
    wait_time_list = []
    current_time = 0
    current_floor = 0
  
    passenger_list, elevator_speed, loading_rate = generate_passengers()
#    elevator_speed = 1
#    loading_rate = 1
    
    print("--"*10, "BEGINNING OF STRATEGY ELEVATOR SIMULATION", "--"*10,file = fp)
    #OUTPUT FORMATTING 
    print(file=fp)
    print("{:<16s}{:<12s}".format("current floor|","t b4 load|" ), end='', file=fp)
    print("{:<9s}{:<12s}".format("load t|", "p onboard|"), end= '',file=fp) 
    print("{:<16s}".format("t after load|"),end='', file=fp)
    print("{:<12s}{:<12s}{:<9s}".format("src floor|", "dst floor|", "move t|" ),\
          end='', file=fp)
    print("{:<15s}".format("t after move|"), end='', file=fp)
    print("{:<12s}{:<11s}{:<16s}".format("p exiting|", "unload t|", "t after exit|"),\
          end='', file=fp)
    print("{:<17s}".format("total t for move|"), file=fp)
    print(file = fp)
    print(file = fp)
        
    elevator_moves = 0
    b = True    #loop control boolean
    while b:
    
        onboard_list, current_time, current_floor, passenger_list, time_b4_loading\
        = load_passengers2(passenger_list, onboard_list, current_time, current_floor,\
                           loading_rate, capacity,fp)
        
        onboard_list, current_time, current_floor = move_passengers2(passenger_list,\
        onboard_list, elevator_speed, current_time, current_floor,fp)
        elevator_moves += 1
        
        onboard_list, current_time, current_floor, wait_time_list = \
        unload_passengers2(onboard_list, loading_rate, current_time, current_floor,\
                           wait_time_list, time_b4_loading,fp)
      
        if len(passenger_list) != 0 and len(onboard_list) != 0:
            b =  True
        if len(passenger_list) == 0:
            if len(onboard_list) == 0:  #check if there's no more people onboard
                b = False
            else:
                b = True
        
        
    print(file = fp)
    print(file = fp)
    print("Total time to deliver all passengers: {:.4f} seconds".format(current_time),file = fp)
    print("Total Number of elevator movements: ", elevator_moves,file = fp)
    
    print(file = fp)
    print("--"*10, "END OF STRATEGY ELEVATOR SIMULATION", "--"*10,file = fp)
    
    return current_time, elevator_moves, wait_time_list

###############################################################################
    
def plot_results(x, y, title, xlabel, ylabel):
    ''' Plots a bar graph of y values with x names '''
    
    pos = range(2)
    pylab.bar(pos, y)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.xticks(pos,x, rotation='90')
    pylab.show()
    

def main():
    ''' Calls random and strategy elevator functions to run simulations '''
    
    fp = open ("single_run.txt", "w")  
    fp2 = open ("multiple_run.txt", "w")
    
    print("--"*36)
    print()
    print()
    print("---"*7, "Real-time Elevator Simulation", "---"*7)
    print()
    print("--"*36)
    
    print(file=fp)
    print("--"*50,file=fp)
    print(file=fp)
    print("---"*9, "Real-time Elevator Simulation", "---"*14, file=fp)
    print(file=fp)
    print("--"*50, file=fp)
       
    print(file=fp)
    print("NOTE: time(seconds) is represented as t", "passenger is represented as p", file=fp)
    
        
    #INPUTS
    while True:     
        try:       
            seed = int(input("Enter seed: ")) 
            numpy.random.seed(seed) 
            break     
        except ValueError:
            print("Invalid input. Please try again!")
            
    while True:   
        try:
            rounds = int(input ("Enter the numbers of rounds to simulate :")) 
            if rounds != 0:
                break   
        except ValueError:
            print("Invalid input. Please try again!")
            
    while True:         
        try:
            capacity = int(input("Enter Elevator Capacity:"))
            break
        except ValueError:
            print("Invalid input. Please try again!")
            
    print()   
    print("{:^50}".format("Running Simulation...")) 
    print() 
               ###SINGLE RUN###
               
    #RandomElevator goes first then StrategyElevator 
    tot_time1, tot_moves1, wait_time_list1 = Random_Elevator(capacity, fp)
    tot_time2, tot_moves2, wait_time_list2 = Strategy_Elevator(capacity, fp)
    
    avg_wait_time1 = sum(wait_time_list1)/len(wait_time_list1)
    avg_wait_time2 = sum(wait_time_list2)/len(wait_time_list2)   
    print(file=fp2)
        
              ###MULTIPLE RUNS###
              
    total_times1_list = []
    total_times2_list = []
    
    total_moves1_list = []
    total_moves2_list = []
    
    averages1= []  #of average wait times
    averages2 = []
    
    R = 0
    R_moves = 0
    S = 0
    S_moves = 0
    
    simulation_count = 0          
    for i in range (rounds):
        
        random.seed(simulation_count)
        tot_time1, tot_moves1, wait_time_list1 = Random_Elevator(capacity, fp)
        total_times1_list.append(tot_time1)
        total_moves1_list.append(tot_moves1)
        
        tot_time2, tot_moves2, wait_time_list2 = Strategy_Elevator(capacity, fp)
        total_times2_list.append(tot_time2)
        total_moves2_list.append(tot_moves2)
        
        simulation_count += 1
        
        #averages
        avg_wait_time1 = sum(wait_time_list1)/len(wait_time_list1)
        avg_wait_time2 = sum(wait_time_list2)/len(wait_time_list2)  
        averages1.append(avg_wait_time1)
        averages2.append(avg_wait_time2) 
        
        if avg_wait_time1 < avg_wait_time2:
            R += 1
        else:
            S += 1
            
        if tot_moves1 < tot_moves2:
            R_moves += 1
        else:
            S_moves += 1
               
    #RandomElevator Stats  
    print(file=fp2)
    print("Random Elevator Statistics", file=fp2)
    print(file=fp2)
    
    random_tot_time_avg = sum(total_times1_list)/len(total_times1_list)
    random_tot_moves_avg = sum(total_moves1_list)/len(total_moves1_list)
    
    print(" average wait time: {:.4f} seconds".format(avg_wait_time1), file=fp2)   
    print(" average total time across all runs: {:.4f} seconds".\
          format(random_tot_time_avg), file=fp2)
    print(" average total elevator moves across all runs: {:.4f} moves".\
          format(random_tot_moves_avg), file=fp2)
    print(" minimum total time across all runs: {} seconds".\
          format(round(min(total_times1_list), 4)), file=fp2)
    print(" maximum total time across all runs: {} seconds".\
          format(round(max(total_times1_list), 4)), file=fp2)
    print(" minimum elevator moves across all runs: {} moves".\
          format(round(min(total_moves1_list), 4)), file=fp2)
    print(" maximum elevator moves across all runs: {} moves".\
          format(round(max(total_moves1_list), 4)), file=fp2)
           
    #StrategyElevator Stats
    print(file=fp2)
    print("Strategy Elevator Statistics", file=fp2)
    print(file=fp2)
    
    strategy_tot_time_avg = sum(total_times2_list)/len(total_times2_list)
    strategy_tot_moves_avg = sum(total_moves2_list)/len(total_moves2_list)
    
    print(" average wait time: {:.4f} seconds".format(avg_wait_time2), file=fp2)
    print(" average total time across all runs: {:.4f} seconds".\
          format(strategy_tot_time_avg), file=fp2)
    print(" average total elevator moves across all runs: {:.4f} moves".\
          format(strategy_tot_moves_avg), file=fp2)
    print(" minimum total time across all runs: {} seconds".\
          format(round(min(total_times2_list), 4)), file=fp2)
    print(" maximum total time across all runs: {} seconds".\
          format(round(max(total_times2_list), 4)), file=fp2)
    print(" minimum elevator moves across all runs: {} moves".\
          format(round(min(total_moves2_list), 4)), file=fp2)
    print(" maximum elevator moves across all runs: {} moves".\
          format(round(max(total_moves2_list), 4)), file=fp2)
            
    #Graphical Representations
    print(file=fp2)
    print("Graphical Results:")
    print(file=fp2)
    
    #Average wait time comparison
    a = ["Random Elevator", "Strategy Elevator"]
    b = [avg_wait_time1, avg_wait_time2]
    
    title = "{}".format("Average Wait Time Comparison")
    xlabel = "Simulation Name"
    ylabel = "Average Wait Time (s)"
    x, y = a, b
    plot_results(x, y, title, xlabel, ylabel)
    
    #Averages of average wait times   
    rand_avg = sum(averages1)/len(averages1)
    stra_avg = sum(averages2)/len(averages2)
    
    g = ["Random Elevator", "Strategy Elevator"]
    h = [rand_avg, stra_avg]
        
    title = "{}".format("Average of Average Wait Times (all runs) Comparison")
    xlabel = "Simulation Name"
    ylabel = "Average Wait Time(s)"
    x, y = g, h
    plot_results(x, y, title, xlabel, ylabel)
       
    #Total times comparison  
    c = ["Random Elevator", "Strategy Elevator"]
    d = [random_tot_time_avg, strategy_tot_time_avg]
    
    title = "{}".format("Average Total Time (all runs) Comparison")
    xlabel = "Simulation Name"
    ylabel = "Average Total Time (s)"
    x, y = c, d
    plot_results(x, y, title, xlabel, ylabel)
    
    #Average elevator moves comparison
    e = ["Random Elevator", "Strategy Elevator"]
    f = [random_tot_moves_avg, strategy_tot_moves_avg]
    
    title = "{}".format("Average Elevator Moves (all runs) Comparison")
    xlabel = "Simulation Name"
    ylabel = "Average Elevator Moves"
    x, y = e, f
    plot_results(x, y, title, xlabel, ylabel)
               
    print(file=fp2)
    print(file=fp2)         
    
    print()
    print("{:^50}".format("Reporting to files..."))
    print() 
    
    
    R_perc =  (R/simulation_count) * 100
    S_perc = (S/simulation_count) * 100
    
    print(" Random Elevator Wins: ", R)
    print(" Strategy Elevator Wins: ", S)
    
    print(" Random Elevator Win Percentage: {:.3f} %".format(R_perc))
    print(" Strategy Elevator Win Percentage: {:.3f} %".format(S_perc))
    
     
    print()
    
    print("--"*10,"{:^10}".format("DONE!"),"--"*10)
    
       
    fp.close()
    fp2.close()
    
                    
if __name__ == "__main__":        
    main()





    
