import random
from os import path
import pickle
import numpy as np
class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0
        self.car_pos = (0,0)
        filename = path.join(path.dirname(__file__),"save","model.pickle")
        with open(filename, 'rb') as file:
            self.clf = pickle.load(file)
        pass

    def update(self, scene_info):
        
        """
        Generate the command according to the received scene information
        """

        
        self.car_pos = scene_info[self.player]
        if len(scene_info[self.player]) == 0:
            return []
        mycar_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center

        
        self.car_pos = scene_info[self.player]
        mycar_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center


        lane_count = [0,0,0,0,0,0,0,0,0]
        row = [0,0,0, 0,0,0]
        col = [0,0]
        leftcar_pos = [self.car_pos[0]-70, self.car_pos[1]]
        rightcar_pos = [self.car_pos[0]+70, self.car_pos[1]]
        for car in scene_info["cars_info"]:
            
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]
            else:  
                car_lane = car["pos"][0] // 70
                
                x = self.car_pos[0] - car["pos"][0] # x relative position
                y = self.car_pos[1] - car["pos"][1] # y relative position
                if y > 0:
                    lane_count[car_lane] = lane_count[car_lane] + 1
                if x <= 45 and x >= -45 :
                    if y > 0:
                        if car["velocity"] < self.car_vel-3:
                            if y < 150:
                                speed_ahead = car["velocity"]
                                row[1] = 1
                        else:
                            if y < 120:
                                speed_ahead = car["velocity"]
                                row[1] = 1
                    else:
                        if y > -120:
                            row[4] = 1 
                        
                leftx = leftcar_pos[0] - car["pos"][0] # x relative position
                y = self.car_pos[1] - car["pos"][1] # y relative position
                if leftx <= 0 and leftx >= -45 :
                    if y > 0:
                        if car["velocity"] < self.car_vel-5:
                            if y < 150:
                                speed_ahead = car["velocity"]
                                row[0] = 1
                        else:
                            if y < 120:
                                speed_ahead = car["velocity"]
                                row[0] = 1
                    else:
                        if y > -100:
                            row[3] = 1

                rightx = rightcar_pos[0] - car["pos"][0] # x relative position
                y = self.car_pos[1] - car["pos"][1] # y relative position
                if rightx <= 45 and rightx >= 0 :
                    if y > 0:
                        if car["velocity"] < self.car_vel-5:
                            if y < 150:
                                speed_ahead = car["velocity"]
                                row[2] = 1
                        else:
                            if y < 120:
                                speed_ahead = car["velocity"]
                                row[2] = 1
                    else:
                        if y > -100:
                            row[5] = 1
        if self.car_pos[0]<=35:
            row[0]=1
            row[3]=1
        if self.car_pos[0]>=595:
            row[2]=1
            row[5]=1

        minvalue = 100
        for i in range(9):
            if lane_count[i] < minvalue:
                minvalue = lane_count[i]
                targetlane = i
            if lane_count[i] == minvalue:
                if lane_count[i] + abs(mycar_lane-i) < minvalue + abs(mycar_lane-targetlane):
                    minvalue = lane_count[i]
                    targetlane = i
                elif lane_count[i] + abs(mycar_lane-i) == minvalue + abs(mycar_lane-targetlane):
                    if abs(5-i) < abs(5-targetlane):
                        minvalue = lane_count[i]
                        targetlane = i
        
        print(lane_count)

        feature = []
        feature.append(mycar_lane)
        feature.append(row[0])
        feature.append(row[1])
        feature.append(row[2])
        feature.append(row[3])
        feature.append(row[4])
        feature.append(row[5])
        feature.append(targetlane)
        feature.append(self.car_vel)
        print(feature)
        feature = np.array(feature)
        feature = feature.reshape((-1,9))

        y = self.clf.predict(feature)   
        print(y)

        if y == 0:
            action = ["SPEED"]
        if  y == 10:
            action = ["SPEED","MOVE_LEFT"]
        if  y == 110:
            action = ["SPEED","MOVE_RIGHT"]
        if  y == 1110:
            action = ["BRAKE","MOVE_LEFT"]
        if  y == 11110:
            action = ["BRAKE","MOVE_RIGHT"]
        if  y == 111110:
            action = ["BRAKE"]
        if targetlane == mycar_lane:
            if lanes[mycar_lane]+2 < self.car_pos[0] and col[0] == 0:
                if not("MOVE_LEFT" in action):
                    action.append("MOVE_LEFT")
            elif lanes[mycar_lane]-2 > self.car_pos[0] and col[1] == 0:
                if not("MOVE_RIGHT" in action):
                    action.append("MOVE_RIGHT")


        return action

        """
        return ["MOVE_LEFT", "MOVE_RIGHT", "SPEED", "BRAKE"]
        """


    def reset(self):
        """
        Reset the status
        """
        pass
