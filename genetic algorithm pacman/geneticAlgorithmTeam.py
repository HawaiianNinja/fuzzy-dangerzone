# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def __init__( self, index, timeForComputing = .1 ):
    """
    Lists several variables you can query:
    self.index = index for this agent
    self.red = true if you're on the red team, false otherwise
    self.agentsOnTeam = a list of agent objects that make up your team
    self.distancer = distance calculator (contest code provides this)
    self.observationHistory = list of GameState objects that correspond
        to the sequential order of states that have occurred so far this game
    self.timeForComputing = an amount of time to give each turn for computing maze distances
        (part of the provided distance calculator)
    """
    # Agent index for querying state
    self.index = index

    # Whether or not you're on the red team
    self.red = None

    # Agent objects controlling you and your teammates
    self.agentsOnTeam = None

    # Maze distance calculator
    self.distancer = None

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None
    
    #depth for expectiMax
    self.depth = 1
  
  def expectiMax(self, state, agent, depth):
    val = 0
    if agent == self.agentCount:
        # if the current agent value is the total number of agents, reset to
        # zero, as this is using a zero based index (0 = pacman)
        agent = self.index
    if  depth == (self.depth * self.agentCount):
        #if our depth limit has been reached (each agent reaches max depth), or we have
        #won or lost, merely evaluate the current position instead of looking ahead
        val = self.evaluationFunction(state)
    elif agent == self.index:
        #pacman
        actions = state.getLegalActions(agent)
        val = float("-inf")
        for action in actions:
            #evaluate all children and take the max value (for pacman)
            val = max(val, self.expectiMax(state.generateSuccessor(agent, action), agent + 1, depth + 1))          
    else:
        #returns returns a random path
        for action in state.getLegalActions(agent):
            #evaluate all children and take the min value (for ghosts)
            val += self.expectiMax(state.generateSuccessor(agent, action), agent + 1, depth + 1)        
        val = val / len(state.getLegalActions(agent))
    return val

  def chooseAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    state = gameState
    self.agentCount = state.getNumAgents()
    depth = 0
    agent = self.index
    avPairs = {}
    actions = state.getLegalActions(agent)
    for action in actions:
        #for each possible direction, run the expectimax algorithm and store a
        #key value pair in the dictionary structure:
        #(value of algorithm, direction of travel)
        #alpha is the best possible score for pacman, and starts at negative infinity
        #beta is the best situation for the ghosts, and starts at positive infinity
        val = self.expectiMax(state.generateSuccessor(agent, action), agent + 1, depth + 1)
        avPairs[val] = action
    #return the direction that yeilds the highest value from expectimax
    return avPairs[max(avPairs)]

  def evaluationFunction(self, currentGameState):
    """
    use values from self.getWeights() to make a better evaluation function!
    """
    weights = self.getWeights(currentGameState)
    pos = currentGameState.getAgentPosition(self.index)
    food = self.getFood(currentGameState)
    protectFood = self.getFoodYouAreDefending(currentGameState)
    powerPellets = self.getCapsules(currentGameState)
    protectedPellets = self.getCapsulesYouAreDefending(currentGameState)
    EnemyPositions = [currentGameState.getAgentPosition(tempAgent) for tempAgent in self.getOpponents(currentGameState)]
    score = 0      
    ghostDistances = []
    for gs in EnemyPositions:
      ghostDistances += [self.getMazeDistance(gs, pos)]
    foodList = food.asList()
    foodDistances = []
    for f in foodList:
      foodDistances += [self.getMazeDistance(pos, f)]
    protectedFoodList = self.getFoodYouAreDefending(currentGameState).asList()
    protectedFoodDistances = []
    for pf in protectedFoodList:
      protectedFoodDistances += [self.getMazeDistance(pos, pf)]
    capsulesDistances = []
    for pp in powerPellets:
        capsulesDistances += [self.getMazeDistance(pos, pp)]
    pCapsulesDistances = []
    for pp in protectedPellets:
        pCapsulesDistances += [self.getMazeDistance(pos, pp)]
    if len(capsulesDistances) > 0:
         score += float(weights['powerPellet'])/(min(capsulesDistances) + 1)
    if len(pCapsulesDistances) > 0:
         score += float(weights['defendPellet'])/(min(pCapsulesDistances) + 1)
    score += float(weights['enemyFood'])/(min(foodDistances) + 1) + float(weights['ourFood'])/(min(protectedFoodDistances) + 1) + (weights['gameScore'] * self.getScore(currentGameState))
    myState = currentGameState.getAgentState(self.index)
    if(myState.isPacman):
      #on enemy side
      if(min(ghostDistances) < 5):
        return -1000
    else:
      # on our side
      if(myState.scaredTimer == 0):
        #not afraid
        score += float(weights['enemy'])/min(ghostDistances)
      else:
        #afraid
        if(min(ghostDistances) < 5):
          return -1000
        else:
          score += float(weights['enemy'])/min(ghostDistances)
    return score
    if self.isScared(currentGameState):
        score -= float(weights['isScared']/min(ghostDistances))
    
    
    if len(foodDistances) != 0:
      #if the list of food distances exists, take the inverse of the minimum
      #and multiply it by the distance to the closest ghost (takes into account
      #best food and nearest opponent)
      if min(ghostDistances) > 6:
        score += ((7) / (min(foodDistances))) ** 2
      else:
        score += ((min(ghostDistances)) / (min(foodDistances))) ** 2

    #add on the score of the to be game state for a flat reference
    score += currentGameState.getScore()
    return score

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return "hi"
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState):
    c = self.chromosome
    return {'enemyFood': c[6], 'ourFood': 0, 'enemy': c[7], 'scaredEnemy': c[8], 'powerPellet': c[9], 'defendPellet':0, 'isScared': 0, 'gameScore': c[10]}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState):
    c = self.chromosome
    return {'enemyFood': 0, 'ourFood': c[0], 'enemy': c[1], 'scaredEnemy': 0, 'powerPellet': c[2], 'defendPellet': c[3], 'isScared': c[4], 'gameScore': c[5]}
