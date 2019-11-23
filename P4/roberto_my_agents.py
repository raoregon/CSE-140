from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core import distanceCalculator
import math
import random


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


class ReflexAgent(CaptureAgent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.
    You are welcome to change it in any way you see fit,
    so long as you don't touch the method headers.
    """

    def __init__(self, index, timeForComputing = 0.1,):
        super().__init__(index)
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

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        `ReflexAgent.getAction` chooses among the best options according to the evaluation function.

        Just like in the previous project, this method takes a
        `pacai.core.gamestate.AbstractGameState` and returns some value from
        `pacai.core.directions.Directions`.
        """
        getCapsules
        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)

        # Choose one of the best actions.
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.

        return legalMoves[chosenIndex]

    def getOpponents(self, gameState):
        """
        Returns agent indices of your opponents. This is the list of the numbers
        of the agents (e.g., red might be 1, 3, 5)
        """

        if self.red:
            return gameState.getBlueTeamIndices()
        else:
            return gameState.getRedTeamIndices()

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

        # newGhostStates = currentGameState.getOpponents()
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        # *** Your Code Here ***

        score = successorGameState.getScore()
        ghostDistance = []
        oldFoodDistance = []
        newFoodDistance = []
        oldPosition = currentGameState.getAgentState(self.index).getPosition()

        # check distance helper function
        def getDistance(x1, y1, x2, y2):
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return distance

        # if ghosts are mean, be wary of them
        """
        for ghosts in newGhostStates:
            ghostDistance.append(getDistance(newPosition[0], newPosition[1],
                                             ghosts.getPosition()[0], ghosts.getPosition()[1]))
        
        if newScaredTimes[0] <= 1:
            if len(ghostDistance) != 0:
                if min(ghostDistance) <= 1.1:
                    return -math.inf
                if min(ghostDistance) <= 1.5:
                    return score - 15
                if min(ghostDistance) < 2:
                    return score - 10
                if min(ghostDistance) < 3:
                    return score - 5
        else:
            if len(ghostDistance) != 0:
                if min(ghostDistance) <= 1.1:
                    return score + 20
                if min(ghostDistance) <= 1.5:
                    return score + 15
                if min(ghostDistance) < 2:
                    return score + 10
                if min(ghostDistance) < 3:
                    return score + 5
        """
        # prioritize moves towards fruit
        for foods in oldFood.asList():
            oldFoodDistance.append(getDistance(oldPosition[0], oldPosition[1], foods[0], foods[1]))

        for foods in oldFood.asList():
            newFoodDistance.append(getDistance(newPosition[0], newPosition[1], foods[0], foods[1]))

        if (len(oldFoodDistance) != 0) and (len(newFoodDistance) != 0):
            if min(newFoodDistance) < min(oldFoodDistance):
                return score + 5

        return score
