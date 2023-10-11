# Predation Model Report

## Background:

### Problem Statement:
The natural world is an endless cycle of predation, as each ecosystem is comprised of a complex food chain that stretches from the lowest plant to the apex predator. This complex system forms the backbone of our environment and understanding how it works is key to preserving its function. A simplistic form of this system can be created thorugh agent based models, where each agent represents an element in the food chain. By adding complex interactions we might achieve further insight into how low level mechanics and behaviours contribute to macro-level outcomes. 

### Importance:


### Overview
This report introduces a simple model of predation that features a number of possible characteristics that result in variations in agent behaviour. Agents are divided into predators and prey, which may freely move on a 2d surface as they pursue their respective goals. By adjusting a number of parameters that describe the behaviours of each agent, we can observe how tendencies in behaviour (like vision, tendency to herd, etc.) can produce results on the population scale.

This model produces a three way relationship between food availability, prey and predator populations that is difficult to exactly measure in the real world. 

## Model Description
This model uses a number of simple rules to produce a complex outcome that roughly models the Lotka–Volterra predator–prey model when we observe its macro trends. By introducing basic interactions that reflect real world phenomena (basic predation mechanics) we recover more complex rules of population growth constraints naturally.


### Rules and Assumptions
As mentioned in the introduction, the model is comprised of two kinds of agents, on a board with randomly placed food. Each entity has a location within the board, and each turn picks a direction in which to move. Which direction is picked, and how the agent moves, is decided by a number of properties that each agent possesses.

Each agent is characterised by:
> bool predator : dictates whether the agent is a predator or not <br />
float vision : dictates how far the agent can perceive predators <br />
float speed : dictates how far an agent will move on each tick <br />
float reproduction probability : dictates how likely an agent is to reproduce after eating <br />
integer age : how old the agent is <br />
integer lifespan : the maximum age of an agent before it dies <br />
float herd factor : dictates how willing agents are to exist near each other <br />

The values are initialised when the agent is born, and only the age value will change over time. Agents are initialised at random positions on the board when the simulation begins, with a user-specified number of predators and prey. From this starting point, they are free to decide which direction they wish to move.

The primary factor contributing to agent direction is food. By default, predators will move directly towards the nearest prey, and prey will move towards the nearest food item on the board. However, this initial vector is influenced by a number of rules.<br />
Firstly, agents will attempt to move away from nearby agents of the same type, according to their herd factor. More specifically, the herd factor dictates the distance at which an agent will begin to move away from another friendly agent. The average of all the vectors pointing away from nearby agents contributes towards the final direction vector. <br />
Secondly, prey agents will attempt to move away from any predator agents that are within their vision. A higher vision parameter will make prey agents run away quicker, as the amount that this rule contributes to overall direction is the inverse of the distance to the predator. (That is, when a predator is very close, the prey will focus on running away, while if the predator is far away the prey will still mostly move towards food.) <br />
Finally, a small amount of noise is added to the final direction vector to make agent tracking less perfect. The amount of noise added to the prey agents is slightly higher than the noise added to predator agents, meaning that in the long run a predator agent will be slightly faster in a straight line, despite having the same move speed. This allows predators to catch prey rather than chasing them forever. 

Each of these rules represents an observable process in real animals, and produces convincing behaviour like herding, scattering and steady population sizes. 

In addition to agent characteristics, there are a few model parameters associated with the board itself, most notably
> float board size : the height and width of the board in arbitrary units <br />
float food frequency : the chance each tick that new food will be added to the board


### Initial Model Configuration:
We understand from real scenarios that predator-prey relationships form fluctuating but persistent population levels. Therefore, in order to produce a convincing result we should aim for the paramters that result in a long running simulation. Once we have determined this, we can then adjust these parameters to focus on other traits like population levels or predator-prey ratios. <br />
As predators naturally have lower population levels in real life, here we have given them a significantly reduced reproduction probability, with only a 25% chance to reproduce upon eating, while prey have a 100% chance. This, combined with an initial predator/prey ratio of 3:1 results in a low but persistent population of predators. <br />
Prey have been given a vision value of 2, which one a board 15 units wide and 15 units high, appears to give them sufficient time to run away without making them too scared to ever go for food. Similarly, the initial herd factor of 0.15 prompts agents to move slightly away from each other, without consistently getting in each others way when they both go for the same food or prey.<br />
An initial lifespan of 80 provides enough time for agents to successfully hunt on the board, but isn't so long that lifespan does not contribute to population dynamics. <br />
On a 15x15 unit board that spawns 1 food every tick, these model parameters produce a simulation that has been observed to run as long as 5000 iterations, and can result in either predators or prey becoming dominant at any time. 

<5000 iteration figure>


## Results

### Initial Model Discussion
The initial model with the parameters discussed above is capable of producing a number of interesting phenomena, and does not always lead to the same outcome. In order to best examine the macro trends in the population over time, I visualised the populations of predators, prey and food over time for each simulation. By examining both the graphs produced by this and the moment to moment simulation behaviour we gain significant insight into how these rules produce complex phenomena. 

Firstly, one of the major trends we can see is the "exchange" of population between predators, prey and food. While in an environment with no predators at all, prey agents only achieve a maximum population of \~150, we see that in an environment with predation this maximum population value can reach as high as 600. This may seem initially unintuitive, as we expect the constant predation to reduce the number of prey agents, but when we examine the simulation in action we see that as predation lowers the prey population, it allows food to accumulate on the board. Once the predator population has fallen due to the reduced number of prey, the prey are able to gather this food and a population explosion occurs. This is one phenomenon produced by the complex relationship between food, predators and prey that governs the overall population as the simulation progresses. <br />
A large number of predators cannot exist without a large number of prey to feed on, or they will die out and their population will return to manageable levels. The same can be said of the relationship between prey and food, where total prey population is limited by the amount of food spawning on the board.

<figure on agents forming herds>

As suggested by the Lotka–Volterra predator–prey model, we also see this population exchange when it comes to predators and prey. Predators can only reproduce when they consume prey, and so an increase in their population necessarily means a reduction in prey population. More interestingly, we see that the limit placed on predator population by the amount of available prey is also related to lifespan. 

### Model Parameter Testing:

lifespan/board size
speed
reproduction


## Conclusion