import random

from pacai.agents.search.multiagent import MultiAgentSearchAgent
import math
from pacai.agents.base import BaseAgent

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

        successorGameState = currentGameState.generatePacmanSuccessor(action)

        # Useful information you can extract.
        newPosition = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.getScaredTimer() for ghostState in newGhostStates]

        # *** Your Code Here ***

        score = successorGameState.getScore()
        ghostDistance = []
        oldFoodDistance = []
        newFoodDistance = []
        oldPosition = currentGameState.getPacmanPosition()

        # check distance helper function
        def getDistance(x1, y1, x2, y2):
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return distance

        # if ghosts are mean, be wary of them

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

        # prioritize moves towards fruit
        for foods in oldFood.asList():
            oldFoodDistance.append(getDistance(oldPosition[0], oldPosition[1], foods[0], foods[1]))

        for foods in oldFood.asList():
            newFoodDistance.append(getDistance(newPosition[0], newPosition[1], foods[0], foods[1]))

        if (len(oldFoodDistance) != 0) and (len(newFoodDistance) != 0):
            if min(newFoodDistance) < min(oldFoodDistance):
                return score + 5

        return score

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
        # return argmax MIN-VALUE(RESULT(state, a))
        value = -math.inf
        legalMoves = gameState.getLegalActions()
        agentIndex = 0

        for action in legalMoves:
            numAgents = gameState.getNumAgents()
            tempValue = self.getMin(gameState.generateSuccessor(agentIndex, action),
                                    self.getTreeDepth(), numAgents - 1)
            if tempValue > value:
                value = tempValue
                bestAction = action

        return bestAction

    def getMax(self, state, depth):
        # if TERMINAL-TEST(state) then return UTILITY(state)
        # check if state is last in depth or if state causes loss
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        # v <- -inf
        value = -math.inf

        # for each a in ACTIONS(state)
        legalMoves = state.getLegalActions()
        successors = []
        agentIndex = 0

        for action in legalMoves:
            successors.append(state.generateSuccessor(agentIndex, action))

        # do: v ←MAX(v, MIN-VALUE(RESULT(s, a)))
        for states in successors:
            numAgents = state.getNumAgents()
            value = max(value, self.getMin(states, depth, numAgents - 1))

        return value

    def getMin(self, state, depth, index):
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        value = math.inf

        legalMoves = state.getLegalActions(index)
        successors = []

        for action in legalMoves:
            successors.append(state.generateSuccessor(index, action))

        for states in successors:
            # check if currently on pacman or ghost, get max if pac, get min if ghost
            if index > 1:
                value = min(value, self.getMin(states, depth - 1, index - 1))
            elif index == 0:
                value = min(value, self.getMax(states, depth))

        return value

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
        super().__init__(index, **kwargs)

    def getAction(self, gameState):
        # v ←MAX-VALUE(state,−∞,+∞)
        value = -math.inf
        alpha = -math.inf
        beta = math.inf
        legalMoves = gameState.getLegalActions()
        agentIndex = 0
        bestAction = []

        for action in legalMoves:

            tempValue = self.getMin(gameState.generateSuccessor(agentIndex, action),
                                    self.getTreeDepth(), agentIndex, alpha, beta)
            if tempValue > value:
                value = tempValue
                bestAction.clear()
                bestAction.append(action)
            elif tempValue == value:
                bestAction.append(action)
            alpha = max(alpha, value)

        return random.choice(bestAction)

    def getMax(self, state, depth, alpha, beta):
        # if TERMINAL-TEST(state) then return UTILITY(state)
        # check if state is last in depth or if state causes loss
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        # v <- -inf
        value = -math.inf

        # for each a in ACTIONS(state)
        legalMoves = state.getLegalActions()
        successors = []
        agentIndex = 0

        for action in legalMoves:
            successors.append(state.generateSuccessor(agentIndex, action))

        # do: v ←MAX(v, MIN-VALUE(RESULT(s, a)))
        for states in successors:
            numAgents = state.getNumAgents()
            value = max(value, self.getMin(states, depth, numAgents - 1, alpha, beta))

            # if v ≥ β then return v
            if value >= beta:
                return value
            # α←MAX(α, v)
            alpha = max(value, alpha)

        return value

    def getMin(self, state, depth, agentIndex, alpha, beta):
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        value = math.inf

        legalMoves = state.getLegalActions(agentIndex)
        successors = []

        for action in legalMoves:
            successors.append(state.generateSuccessor(agentIndex, action))

        for states in successors:
            # check if currently on pacman or ghost, get max if pac, get min if ghost
            if agentIndex > 1:
                value = min(value, self.getMin(states, depth, agentIndex - 1, alpha, beta))
            elif agentIndex == 0:
                value = min(value, self.getMax(states, depth - 1, alpha, beta))

            # if v ≤ α then return v
            if value <= alpha:
                return value
            # β←MIN(β, v)
            beta = min(value, beta)

        return value

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
        super().__init__(index, **kwargs)

    def getAction(self, gameState):

        value = -math.inf
        agentIndex = 0

        numAgents = gameState.getNumAgents()
        legalMoves = gameState.getLegalActions()

        for action in legalMoves:
            tempValue = self.expectedValue(gameState.generateSuccessor(agentIndex, action),
                                      self.getTreeDepth(), numAgents - 1)
            if tempValue > value:
                value = tempValue
                bestAction = action

        return bestAction

    def getMax(self, state, depth):
        # if TERMINAL-TEST(state) then return UTILITY(state)
        # check if state is last in depth or if state causes loss
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        # v <- -inf
        value = -math.inf

        # for each a in ACTIONS(state)
        legalMoves = state.getLegalActions()
        successors = []
        agentIndex = 0

        for action in legalMoves:
            successors.append(state.generateSuccessor(agentIndex, action))

        # do: v ←MAX(v, MIN-VALUE(RESULT(s, a)))
        for states in successors:
            numAgents = state.getNumAgents()
            value = max(value, self.expectedValue(states, depth, numAgents - 1))

        return value

    def expectedValue(self, state, depth, agentIndex):
        if depth == 0 or state.isLose():
            return self.getEvaluationFunction()(state)

        value = 0

        legalMoves = state.getLegalActions(agentIndex)
        successors = []

        for action in legalMoves:
            successors.append(state.generateSuccessor(agentIndex, action))
        div = len(successors)

        for states in successors:
            if agentIndex > 1:
                value += self.expectedValue(states, depth, agentIndex - 1) / div
            elif agentIndex == 0:
                value += self.getMax(states, depth - 1)
        return value

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
