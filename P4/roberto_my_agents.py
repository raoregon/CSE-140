from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
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

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def chooseAction(self, gameState):
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
        # print(bestScore)
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
        currentPosition = currentGameState.getAgentState(self.index).getPosition()
        newPosition = successorGameState.getAgentState(self.index).getPosition()
        foodPosition = self.getFood(currentGameState)

        #distancer = Distancer(currentGameState.getInitialLayout())

        # newGhostStates = currentGameState.getOpponents()
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        # *** Your Code Here ***

        score = successorGameState.getScore()
        ghostDistance = []
        oldFoodDistance = []
        newFoodDistance = []
        oldPosition = currentGameState.getAgentState(self.index).getPosition()

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
        for foods in foodPosition.asList():
            oldFoodDistance.append(self.getMazeDistance(currentPosition, foods))

        for foods in foodPosition.asList():
            newFoodDistance.append(self.getMazeDistance(newPosition, foods))

        if (len(oldFoodDistance) != 0) and (len(newFoodDistance) != 0):
            if min(newFoodDistance) < min(oldFoodDistance):
                return score + 5

        return score
