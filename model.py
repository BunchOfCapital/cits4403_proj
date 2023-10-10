'''
Written by Joel Wildman (22984156)


ant/animal foraging

set of agents with size, speed, vision, hunger, reproduction? etc

each tick they decide on a vector

food generated in the environment
	environment has different difficulties of traversal? (speed modifier)
		agent characteristic for difficult terrain traversal? (modify the modifier)

agents return food to nest or pack behaviour?


'''


# agent object

# 10x10 environment

# initialise agents

# run simulation
# 	agents check their surroundings
# 	move towards goal
# 		normalised vector (are predators faster? does prey run?)
# 	if no goal, move forward with random distribution
# 	check agent age?
# 	check agent reproduction status?
# 		agent have set chance to reproduce when eating?
# 			herbivores will have higher chance than carnivores

# render simulation

import numpy as np
from matplotlib import pyplot as plt
import math
import threading
import time
import sys

BOARD_SIZE = 10

STATS_BUFFER = {
	'predators':[],
	'prey':[],
	'total_pop':[],
	'avg_age':[],
	'food':[]
}


#agent object for all alive objects on the board
class Agent(object):
	predator = False
	vision = 2
	speed = 0.3
	reproduction_prob = 0.5
	age = 0
	lifespan = 80
	#somewhat counterintuitive, but higher herd factor means LESS clumping
	herd_factor = 0.15
	direction = np.clip(np.random.rand(2), -1, 1)
	location = np.zeros(2)

	def __init__(self, predator, location):
		self.predator = predator
		self.location = location

#calculate pythagorean distance between two agents
def calc_dist(location1, location2):
	xdist = abs(location1[0] - location2[0])
	ydist = abs(location1[1] - location2[1])

	hdist = np.sqrt(xdist**2 + ydist**2)

	#to avoid dividing by 0 later, we catch that scenario here and assume it's just a very small number
	if (hdist == 0):
		hdist = 0.0001
	return hdist

#normalises a vector to a unit vector
#courtesy of https://stackoverflow.com/questions/21030391/how-to-normalize-a-numpy-array-to-a-unit-vector
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

#rotates a vector by angle radians
#courtesy of https://learnpainless.com/how-to-rotate-and-scale-a-vector-in-python/
def rotate_vector(vector, angle):
    x = vector[0] * math.cos(angle) - vector[1] * math.sin(angle)
    y = vector[0] * math.sin(angle) + vector[1] * math.cos(angle)
    return np.array([x, y])

#returns the average of two vectors
def vector_avg(vec1, vec2):
	avg = (vec1 + vec2) / 2
	return avg

#takes two points and returns the normalized vector pointing from point1 to point2
def points_2_vec(point1, point2):
	x = point2[0] - point1[0]
	y = point2[1] - point1[1]
	new_vec = normalize(np.array([x,y]))
	return new_vec


#create n predators and p prey with random positions on the board
def gen_agents(num_pred, num_prey):
	agents = []

	for i in range(num_pred):
		loc = np.random.rand(2)
		loc = loc * BOARD_SIZE #scale location to be anywhere within the board
		agents.append(Agent(predator=True, location=loc))

	for i in range(num_prey):
		loc = np.random.rand(2)
		loc = loc * BOARD_SIZE #scale location to be anywhere within the board 
		agents.append(Agent(predator=False, location=loc))

	return agents

#execute a single iteration of the sim, agents will 
	#die of old age
	#move and pick a new direction
	#feed
	#reproduce
def iterate_sim(agents, food, food_frequency):

	#kill old agents, age young ones
	agents = [agent for agent in agents if (agent.age <= agent.lifespan)]
	for agent in agents:
		agent.age += 1


	#for each agent, move and then decide on new heading for this tick
	#predators move towards closest prey
	if (len(agents) == 0):
		return agents, food


	for i in range(len(agents)):

		#PREDATOR ACTIONS
		if (agents[i].predator):
			closest_agent = None
			closest_dist = 50 #beyond max environment size

			away_vec = agents[i].direction
			#find closest prey agent
			for j in range(len(agents)):
				dist = calc_dist(agents[i].location, agents[j].location)
				if (not agents[j].predator):
					if (i != j and dist < closest_dist):
						closest_agent = agents[j]
						closest_dist = dist
				else:
					if (dist < agents[i].vision * agents[i].herd_factor):
						agent_dir = points_2_vec(agents[j].location, agents[i].location)
						away_vec = normalize(vector_avg(away_vec, agent_dir * min(agents[i].vision/dist, 1)))

			if (closest_agent != None):
				#move towards it, max speed of 1
				agents[i].direction = (normalize(agents[i].location - closest_agent.location)) * (-1) * agents[i].speed


			agents[i].direction = normalize(vector_avg(agents[i].direction, away_vec*agents[i].herd_factor))
			#add a little bit of noise
			rot = np.random.normal(loc=0.0, scale = math.pi/30)
			agents[i].direction = normalize(rotate_vector(agents[i].direction, rot)) * agents[i].speed

		#PREY ACTIONS
		else:
			#prey moves towards nearest food with some noise
			closest_food = None
			food_dist = 50 #beyond max environment size
			for j in range(len(food)):
				dist = calc_dist(agents[i].location, food[j])
				if (dist < food_dist):
					closest_food = j
					food_dist = dist

			#move towards food
			agents[i].direction = (normalize(agents[i].location - food[closest_food])) * (-1) * agents[i].speed

			#move away from nearby predators according to vision, away from friendlies according to herd factor
			away_vec = agents[i].direction
			for j in range(len(agents)):
				dist = calc_dist(agents[i].location, agents[j].location)
				if agents[j].predator:
					if (dist < agents[i].vision):
						#average our vector and predator vector, scaled by our proximity 
						agents[i].direction = normalize(vector_avg(agents[i].direction * min(dist/agents[i].vision, 1), agents[j].direction * min(agents[i].vision/dist, 1)))
				else:
					if (dist < agents[i].vision * agents[i].herd_factor):
						agent_dir = points_2_vec(agents[j].location, agents[i].location)
						away_vec = normalize(vector_avg(away_vec, agent_dir * min(agents[i].vision/dist, 1)))
			agents[i].direction = normalize(vector_avg(agents[i].direction, away_vec*agents[i].herd_factor))

			#add a little bit of random noise, more than the predators to slow them down
			rot = np.random.normal(loc=0.0, scale = math.pi/10)
			agents[i].direction = normalize(rotate_vector(agents[i].direction, rot)) * agents[i].speed


		#move the agent according to heading
		agents[i].location = np.clip(agents[i].location + agents[i].direction, 0, BOARD_SIZE)


	#now we check if any prey got caught, or found food
	alive_agents = []
	dead_agents = []
	new_food = []
	food_eaten = []

	#the required proximity to interact must be at least speed/2, or agents can get stuck in a loop
	proximity = agents[0].speed/2
	for i in range(len(agents)):
		#predators catch prey
		if (agents[i].predator):
			for j in range(len(agents)):
				if (not agents[j].predator and calc_dist(agents[i].location, agents[j].location) < proximity):
					dead_agents.append(j)
					#reproduce if called for, but at a lower chance than prey
					if (np.random.rand() < agents[i].reproduction_prob/2):
						alive_agents.append(Agent(predator=True, location=agents[i].location))

		#prey eats food
		else:
			for j in range(len(food)):
				if (calc_dist(agents[i].location, food[j]) < proximity):
					#eat the food and maybe reproduce, at a high chance
					food_eaten.append(j)
					if (np.random.rand() < agents[i].reproduction_prob*2):
						alive_agents.append(Agent(predator=False, location=agents[i].location))

	#update food and agent lists
	for i in range(len(agents)):
		if (i not in dead_agents):
			alive_agents.append(agents[i])

	for i in range(len(food)):
		if (i not in food_eaten):
			new_food.append(food[i])

	if (np.random.rand() < food_frequency):
		new_food.append(np.random.rand(2)*BOARD_SIZE)

	return alive_agents, np.array(new_food)


def scheduler(agents):
	return 0

def draw_sim(agents):
	cmap = []
	locs = np.zeros((len(agents), 2))
	for i in range(len(agents)):
		if agents[i].predator:
			cmap.append('red')
		else:
			cmap.append('blue')
		locs[i] = agents[i].location[:]

	return cmap, locs

def collect_stats(agents, food):
	predators = 0
	prey = 0
	avg_age = 0
	for i in range(len(agents)):
		if agents[i].predator:
			predators += 1
		else:
			prey += 1

		avg_age += agents[i].age
	avg_age = avg_age/len(agents)

	STATS_BUFFER['predators'].append(predators)
	STATS_BUFFER['prey'].append(prey)
	STATS_BUFFER['total_pop'].append(predators+prey)
	STATS_BUFFER['avg_age'].append(avg_age)
	STATS_BUFFER['food'].append(len(food))
	return 0


def main(iterations, num_prey, num_predators, food_frequency):
	agents = gen_agents(num_predators, num_prey)
	#one food for each prey to start
	food = np.random.rand(num_prey, 2)*BOARD_SIZE
	#30 fps or so
	interval = 0.03
	

	#plt.ion()
	fig, axes = plt.subplots()
	

	cmap, locs = draw_sim(agents)
	im = axes.scatter(locs[:,0],locs[:,1], c=cmap)
	im2 = axes.scatter(food[:,0], food[:,1], c='green')


	pop_label = axes.text(0.3,0.02,"Population: " + str(num_prey+num_predators),transform=fig.transFigure)
	fps_label = axes.text(0.5,0.02,"FPS: -",transform=fig.transFigure)
	iter_label = axes.text(0.1,0.02,"Iteration: -",transform=fig.transFigure)

	plt.xlim(0,BOARD_SIZE)
	plt.ylim(0,BOARD_SIZE)

	fig.canvas.draw()
	plt.pause(0.1)

	background = fig.canvas.copy_from_bbox(axes.bbox)

	start_time = time.time()
	FPS = 0
	prev_frame = 0
	current_frame = 0
	frame_time = 0
	print("Starting simulation...")
	for i in range(iterations):
		
		agents, food = iterate_sim(agents, food, food_frequency)

		collect_stats(agents, food)

		pop_label.set_text("Population: " + str(len(agents)))
		fps_label.set_text("FPS: "+ str(round(FPS, 2)))
		iter_label.set_text("Iteration: "+str(i))

		#draw it
		cmap, locs = draw_sim(agents)

		im.set_offsets(np.c_[locs[:,0],locs[:,1]])
		im2.set_offsets(np.c_[food[:,0],food[:,1]])
		im.set_color(cmap)

		fig.canvas.flush_events()
		#fig.canvas.draw_idle()

		#calculate FPS
		prev_frame = current_frame
		current_frame = time.time()
		frame_time = current_frame - prev_frame
		FPS = 1 / frame_time

		plt.pause(0.001)


	fig2, axes2 = plt.subplots()
	im3, = axes2.plot(STATS_BUFFER['predators'], 'r-', label='Predators')
	im4, = axes2.plot(STATS_BUFFER['prey'], 'b-', label='Prey')
	im5, = axes2.plot(STATS_BUFFER['food'], 'g-', label='Food')
	fig2.show()
	plt.pause(0.001)
	input()
	print("Done.")

if __name__ == '__main__':
	main(100, num_prey=30, num_predators=10, food_frequency=1)

