from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent

import random

from pacai.agents.base import BaseAgent
from pacai.agents.search.multiagent import MultiAgentSearchAgent
import math

def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.student.myTeam.ReflexAgent',
        second = 'pacai.student.myTeam.ReflexAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    
    firstAgent = reflection.qualifiedImport(first)
    secondAgent = reflection.qualifiedImport(second)

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]

class ReflexAgent(BaseAgent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.
    You are welcome to change it in any way you see fit,
    so long as you don't touch the method headers.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        `ReflexAgent.getAction` chooses among the best options according to the evaluation function.

        Just like in the previous project, this method takes a
        `pacai.core.gamestate.AbstractGameState` and returns some value from
        `pacai.core.directions.Directions`.
        """

        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)

        # Choose one of the best actions.
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current `pacai.bin.pacman.PacmanGameState`
        and an action, and returns a number, where higher numbers are better.
        Make sure to understand the range of different values before you combine them
        in your evaluation function.
        """

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Useful information you can extract.
        newPosition = successorGameState.getAgentState(self.index).getPosition()
        oldFood = currentGameState.getFood()
        #newGhostStates = successorGameState.getGhostStates()
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        # # *** Your Code Here ***

        value = successorGameState.getScore()
        Dist_of_Ghost = []
        # for ghost in newGhostStates:
        #     Dist_of_Ghost.append(math.sqrt(pow(newPosition[0] - ghost.getPosition()[0], 2)
        #         + pow(newPosition[1] - ghost.getPosition()[1], 2)))
        # if len(Dist_of_Ghost) != 0:
        #     if ghost.getScaredTimer() != 0:
        #         if min(Dist_of_Ghost) <= 3:
        #             value += 10
        #     else:
        #         if min(Dist_of_Ghost) < 2:
        #             return - (float('inf'))

        if len(oldFood.asList()) > len(successorGameState.getFood().asList()):
            value += 10

        newFood = successorGameState.getFood()
        # new_food_dist = [math.sqrt(pow(newPosition[0] - food_pos[0], 2)
        #  + pow(newPosition[1] - food_pos[1], 2))
        #     for food_pos in newFood.asList()]

        oldPos = currentGameState.getAgentState(self.index).getPosition()
        # old_food_dist = [math.sqrt(pow(oldPos[0] - food_pos[0], 2)
        #     + pow(oldPos[1] - food_pos[1], 2))
        #     for food_pos in oldFood.asList()]

        new_food_dist = []
        for food_pos in newFood.asList():
            new_food_dist.append(CaptureAgent.getMazeDistance(self, newPosition, food_pos))
        
        old_food_dist = []
        for food_pos in oldFood.asList():
            old_food_dist.append(CaptureAgent.getMazeDistance(self, oldPos, food_pos))

        # making sure that there is elements in the list new_food_dist
        if not not new_food_dist:
            value -= min(new_food_dist)
            if min(new_food_dist) == min(old_food_dist):
                value -= 2

        if (newPosition == oldPos):
            value -= 3

        return value
