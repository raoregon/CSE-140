import random

from pacai.agents.base import BaseAgent
from pacai.agents.search.multiagent import MultiAgentSearchAgent

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
        legalMoves = gameState.getLegalActions()

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

        # Useful information you can extract.
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPosition = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        # newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        # *** Your Code Here ***
        ghostDistance = [abs(newPosition[0] - ghost.getPosition()[0])
        + abs(newPosition[1] - ghost.getPosition()[1]) for ghost in newGhostStates]
        if len(ghostDistance) != 0:
            if min(ghostDistance) <= 2:
                return - (float('inf'))

        value = successorGameState.getScore()

        # if scared ghost nearby go towards it
        ghostDistance = [abs(newPosition[0] - ghost.getPosition()[0])
        + abs(newPosition[1] - ghost.getPosition()[1]) for ghost in newGhostStates]
        if len(ghostDistance) != 0:
            if min(ghostDistance) <= 3:
                value += 10

        if len(successorGameState.getFood().asList()) < len(oldFood.asList()):
            value += 10

        newFoodDist = [abs(newPosition[0] - food[0]) + abs(newPosition[1] - food[1])
        for food in successorGameState.getFood().asList()]
        oldFoodDist = [abs(currentGameState.getPacmanPosition()[0] - food[0])
        + abs(currentGameState.getPacmanPosition()[1]
        - food[1]) for food in currentGameState.getFood().asList()]
        # go towards food but try not to keep going back and forth
        if len(newFoodDist) != 0:
            value -= min(newFoodDist)
            if min(newFoodDist) == min(oldFoodDist):
                value -= 2

        if (newPosition == currentGameState.getPacmanPosition()):
            value -= 2

        return value

class MinimaxAgent(MultiAgentSearchAgent):
    """
    A minimax agent.

    Here are some method calls that might be useful when implementing minimax.

    `pacai.core.gamestate.AbstractGameState.getNumAgents()`:
    Get the total number of agents in the game

    `pacai.core.gamestate.AbstractGameState.getLegalActions`:
    Returns a list of legal actions for an agent.
    Pacman is always at index 0, and ghosts are >= 1.

    `pacai.core.gamestate.AbstractGameState.generateSuccessor`:
    Get the successor game state after an agent takes an action.

    `pacai.core.directions.Directions.STOP`:
    The stop direction, which is always legal, but you may not want to include in your search.

    Method to Implement:

    `pacai.agents.base.BaseAgent.getAction`:
    Returns the minimax action from the current gameState using
    `pacai.agents.search.multiagent.MultiAgentSearchAgent.getTreeDepth`
    and `pacai.agents.search.multiagent.MultiAgentSearchAgent.getEvaluationFunction`.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getAction(self, gameState):
        # *** Your Code Here ***
        MAX = -(float('inf'))
        for action in gameState.getLegalActions():
            temp = self.getMin(gameState.generateSuccessor(0, action),
            self._treeDepth, gameState.getNumAgents() - 1)
            if temp > MAX:
                MAX = temp
                direction = action

        return direction

    def getMax(self, state, depth):
        if state.isLose() or state.isWin() or depth == 0:
            return self._evaluationFunction(state)

        MAX = -(float('inf'))
        legalActions = state.getLegalActions()
        successors = []
        for action in legalActions:
            successors.append(state.generateSuccessor(0, action))

        for successorState in successors:
            MAX = max(MAX, self.getMin(successorState, depth, successorState.getNumAgents() - 1))

        return MAX

    def getMin(self, state, depth, index):
        if state.isLose() or state.isWin() or depth == 0:
            return self._evaluationFunction(state)

        MIN = float('inf')
        legalActions = state.getLegalActions(index)
        successors = []
        for action in legalActions:
            successors.append(state.generateSuccessor(index, action))
        for successorState in successors:
            if index > 1:
                MIN = min(MIN, self.getMin(successorState, depth, index - 1))
            else:
                MIN = min(MIN, self.getMax(successorState, depth - 1))

        return MIN

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    A minimax agent with alpha-beta pruning.

    Method to Implement:

    `pacai.agents.base.BaseAgent.getAction`:
    Returns the minimax action from the current gameState using
    `pacai.agents.search.multiagent.MultiAgentSearchAgent.getTreeDepth`
    and `pacai.agents.search.multiagent.MultiAgentSearchAgent.getEvaluationFunction`.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        def maxValue(agent, depth, gameState, a, b):
            v = -float('Inf')
            for newState in gameState.getLegalActions(agent):
                v = max(v, abPruning(1, depth, gameState.generateSuccessor(agent, newState), a, b))
                if v > b:
                    return v
                a = max(a, v)
            return v

        def minValue(agent, depth, gameState, a, b):
            v = float('Inf')

            nextAgent = agent + 1
            if gameState.getNumAgents() == nextAgent:
                nextAgent = 0
            if nextAgent == 0:
                depth += 1

            for newState in gameState.getLegalActions(agent):
                v = min(v, abPruning(nextAgent, depth,
                gameState.generateSuccessor(agent, newState), a, b))
                if v < a:
                    return v
                b = min(b, v)
            return v

        def abPruning(agent, depth, gameState, a, b):
            if gameState.isLose() or gameState.isWin() or depth == 0:
                return self._evaluationFunction(gameState)

            if agent == 0:
                return maxValue(agent, depth, gameState, a, b)
            else:
                return minValue(agent, depth, gameState, a, b)

        Maximum = -float('Inf')
        a = -float('Inf')
        b = float('Inf')
        for agentState in gameState.getLegalActions(0):
            ghostValue = abPruning(1, 0, gameState.generateSuccessor(0, agentState), a, b)
            if ghostValue > Maximum:
                Maximum = ghostValue
                action = agentState
            if Maximum > b:
                return Maximum
            a = max(a, Maximum)

        return action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    An expectimax agent.

    All ghosts should be modeled as choosing uniformly at random from their legal moves.

    Method to Implement:

    `pacai.agents.base.BaseAgent.getAction`:
    Returns the expectimax action from the current gameState using
    `pacai.agents.search.multiagent.MultiAgentSearchAgent.getTreeDepth`
    and `pacai.agents.search.multiagent.MultiAgentSearchAgent.getEvaluationFunction`.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.treeDepth and self.evaluationFunction
        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """

        # *** Your Code Here ***

        MAX = -(float('inf'))

        for action in gameState.getLegalActions():
            temp = self.expectedValue(gameState.generateSuccessor(0, action),
            self._treeDepth, gameState.getNumAgents() - 1)
            if temp > MAX:
                MAX = temp
                direction = action

        return direction

    def max_value(self, state, depth):
        if state.isLose() or state.isWin() or depth == 0:
            return self._evaluationFunction(state)

        MAX = -(float('inf'))
        legalActions = state.getLegalActions()
        successors = []
        for action in legalActions:
            successors.append(state.generateSuccessor(0, action))

        for successorState in successors:
            MAX = max(MAX,
            self.expectedValue(successorState, depth, successorState.getNumAgents() - 1))

        return MAX

    def expectedValue(self, state, depth, index):
        if state.isLose() or state.isWin() or depth == 0:
            return self._evaluationFunction(state)

        legalActions = state.getLegalActions(index)
        successors = []
        for action in legalActions:
            successors.append(state.generateSuccessor(index, action))
        total = 0
        for successorState in successors:
            if index > 1:
                total = total + self.expectedValue(successorState,
                depth, index - 1) / len(successors)
            else:
                total = self.max_value(successorState, depth - 1)

        return total

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable evaluation function.

    DESCRIPTION: <write something here so we know what you did>
    """
    return currentGameState.getScore()

class ContestAgent(MultiAgentSearchAgent):
    """
    Your agent for the mini-contest.

    You can use any method you want and search to any depth you want.
    Just remember that the mini-contest is timed, so you have to trade off speed and computation.

    Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
    just make a beeline straight towards Pacman (or away if they're scared!)

    Method to Implement:

    `pacai.agents.base.BaseAgent.getAction`
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

