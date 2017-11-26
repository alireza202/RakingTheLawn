import sys
import numpy as np

import matplotlib.pyplot as plt

class Lawn:
    
    def __init__(self, config):
        '''
        m the number of cells in the direction of left to right
        n the number of cells in the direction of down to up
        '''
        self.m = config['m']
        self.n = config['n']
        
        self.capacity = config['cell_capacity']
        self.initial_seed = config['initial_seed']
        self.random_seed = config['random_seed']
        
        if not self.random_seed:
            self.cells = self.initial_seed * np.ones((self.m, self.n))
        else:
            self.cells = np.random.poisson(lam=self.initial_seed, size=(self.m, self.n))
    
    
    def update_rake(self, moved_leaves, x, y, target_x, target_y):
        
        # every cell has a capacity
        target_capacity = self.capacity - self.cells[target_x, target_y]
        moved_leaves = min(moved_leaves, target_capacity)
        
        # update current cell
        self.cells[x, y] -= moved_leaves
        # update target cell
        self.cells[target_x, target_y] += moved_leaves
       
    
    def update_collect(self, collected_leaves, x, y):
        
        self.cells[x, y] -= collected_leaves


class Robot:
    
    def __init__(self, config):
        
        x = config['init_x']
        y = config['init_y']
        
        self.x_lim = [0, config['m'] - 1]
        self.y_lim = [0, config['n'] - 1]
        
        self.move_reward = config['move_reward']
        self.energy = config['initial_energy']
        
        if x > self.x_lim[1] or x < self.x_lim[0] or y > self.y_lim[1] or y < self.y_lim[0]:
            raise ValueError('x and y should be within the lawn limits.')
        else:
            self.x = x
            self.y = y
        
    def whereis(self):
        
        print 'robot is at %d, %d.' % (self.x, self.y)
    
    
    def move(self, direction):
        '''
        direction is a number (0, 1, 2, 3) corresponding to down, up, left, right
        '''
        
        if self.energy > np.abs(self.move_reward):
            if direction == 0 and self.y > self.y_lim[0]:
                self.y -= 1
            elif direction == 1 and self.y < self.y_lim[1]:
                self.y += 1
            elif direction == 2 and self.x > self.x_lim[0]:
                self.x -= 1
            elif direction == 3 and self.x < self.x_lim[1]:
                self.x += 1
                
            return self.reward()
        else:
            sys.exit('robot has no energy to move.')
            
            
    def reward(self):
        
        self.energy += self.move_reward
        return self.move_reward
            

class Rake:
    
    def __init__(self, config):
        
        self.success_rate = config['rake_success_rate']
        self.capacity = config['rake_capacity']
        self.rake_reward = config['rake_reward']
        
    def rake(self, robot, lawn, direction):
        '''
        updates lawn where robot is, given the direction
        '''
        x, y = robot.x, robot.y
        
        # there is a capacity for raking
        moved_leaves = self.success_rate * lawn.cells[x, y]
        moved_leaves = min(moved_leaves, self.capacity)
        
        if robot.energy > np.abs(self.rake_reward):
            if direction == 0 and y > robot.y_lim[0]:
                lawn.update_rake(moved_leaves, x, y, x, y - 1)
            elif direction == 1 and y < robot.y_lim[1]:
                lawn.update_rake(moved_leaves, x, y, x, y + 1)
            elif direction == 2 and x > robot.x_lim[0]:
                lawn.update_rake(moved_leaves, x, y, x - 1, y)
            elif direction == 3 and x < robot.x_lim[1]:
                lawn.update_rake(moved_leaves, x, y, x + 1, y)
                
            return self.reward(robot)
        else:
            sys.exit('robot has no energy to rake.')
        
        
    def reward(self, robot):
        robot.energy += self.rake_reward
        return self.rake_reward
    
    
class Collect:
    
    def __init__(self, config):
        
        self.success_rate = config['collect_success_rate']
        self.capacity = config['collect_capacity']
        self.collect_reward = config['collect_reward']
       
    
    def collect(self, robot, lawn):
        
        x, y = robot.x, robot.y
        
        # there is a capacity for collecting
        collected_leaves = min(self.success_rate * lawn.cells[x, y], self.capacity)
        
        if robot.energy > np.abs(self.collect_reward[0]):
            lawn.update_collect(collected_leaves, x, y)
            return self.reward(collected_leaves, robot)
        else:
            sys.exit('robot has no energy to collect.')
        
    
    def reward(self, collected_leaves, robot):
        '''
        collection has two rewards: a negative reward for the act of collecting,
            and a positive reward proportional to the number of collected leaves.
        '''
        robot.energy += self.collect_reward[0]
        return self.collect_reward[0] + self.collect_reward[1] * collected_leaves
    
    
def plot_lawn(lawn, robot, fig_size = (6,8)):
    plt.figure(figsize = fig_size)
    plt.imshow(lawn.cells.T, interpolation='nearest', origin='lower')
    plt.plot([robot.x], [robot.y], marker='o', markersize=8, color="white")
    plt.xlim([0, lawn.m])
    plt.ylim([0, lawn.n])
    plt.colorbar()