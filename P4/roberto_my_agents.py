from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.util import counter
from pacai.core.directions import Directions
import random
import math


def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.student.myTeam.UngaBungaAgent',
        second = 'pacai.student.myTeam.UngaBungaAgent'):
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


class UngaBungaAgent(CaptureAgent):
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
        scores = [self.evaluate(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.
        # print(bestScore)
        return legalMoves[chosenIndex]
    """
    def evaluationFunction(self, currentGameState, action):

        successorGameState = currentGameState.generateSuccessor(self.index, action)

        # Positions: current, successor, food
        currentPosition = currentGameState.getAgentState(self.index).getPosition()
        newPosition = successorGameState.getAgentState(self.index).getPosition()
        foodPosition = self.getFood(currentGameState)

        enemyIndex = self.getOpponents(currentGameState)
        newEnemyIndex = self.getOpponents(successorGameState)

        enemyStates = []
        enemyPositions = []
        newEnemyStates = []
        newEnemyPositions = []

        for opponentIndex in enemyIndex:
            enemyState = currentGameState.getAgentState(opponentIndex)
            enemyStates.append(enemyState)

        for opponentIndex in newEnemyIndex:
            newEnemyState = successorGameState.getAgentState(opponentIndex)
            newEnemyStates.append(newEnemyState)

        for states in enemyStates:
            enemyPositions.append(states.getPosition())

        for states in newEnemyStates:
            newEnemyPositions.append(states.getPosition())

        score = successorGameState.getScore()
        enemyDistance = []
        oldFoodDistance = []
        newFoodDistance = []

        # if ghosts are mean, be wary of them

        for enemies in newEnemyStates:
            enemyDistance.append(self.getMazeDistance(currentPosition, enemies.getPosition()))

        if len(enemyDistance) != 0:
            if min(enemyDistance) <= 1.1:
                return -math.inf
            if min(enemyDistance) <= 1.5:
                return score - 15
            if min(enemyDistance) < 2:
                return score - 10
            if min(enemyDistance) < 3:
                return score - 5


        # prioritize moves towards fruit
        for foods in foodPosition.asList():
            oldFoodDistance.append(self.getMazeDistance(currentPosition, foods))

        for foods in foodPosition.asList():
            newFoodDistance.append(self.getMazeDistance(newPosition, foods))

        if (len(oldFoodDistance) != 0) and (len(newFoodDistance) != 0):
            if min(newFoodDistance) < min(oldFoodDistance):
                return score + 5

        return score
    """

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)

        return features * weights

    def getFeatures(self, gameState, action):
        features = counter.Counter()
        successor = gameState.generateSuccessor(self.index, action)
        features['successorScore'] = self.getScore(successor)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        # check how many agents are on our team
        # split up team to Attackers and Defenders depending on size
        # half attack, half defense
        features['onDefense'] = 0

        currentTeam = self.getTeam(gameState)
        teamLength = len(currentTeam)

        if teamLength % 2 == 0:
            count = 1
            while count <= teamLength:
                if count % 2 == 0:
                    features['onDefense'] = 1
                count += 1

        # % of our food vs their food
        ourFoodPosition = self.getFoodYouAreDefending(gameState)
        theirFoodPosition = self.getFood(gameState)
        ourFoodCount = 0
        theirFoodCount = 0

        for foods in ourFoodPosition:
            for food in foods:
                if str(food) == "True":
                    ourFoodCount += 1
        for foods in theirFoodPosition:
            for food in foods:
                if str(food) == "True":
                    theirFoodCount += 1

        ourFoodMoreOrEqual = ourFoodCount >= theirFoodCount

        # if on Offense:
        if features['onDefense'] == 0:
            print("on offense")
            # Compute distance to the nearest food.
            foodList = self.getFood(successor).asList()

            # This should always be True, but better safe than sorry.
            if len(foodList) > 0:
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

            return features

        # if on defense
        elif features['onDefense'] == 1:
            # Computes distance to invaders we can see.
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
            features['numInvaders'] = len(invaders)

            if len(invaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)

            if action == Directions.STOP:
                features['stop'] = 1

            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if action == rev:
                features['reverse'] = 1

            return features

    def getWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        features = self.getFeatures(gameState, action)
        if features['onDefense'] == 0:
            return {
                'successorScore': 100,
                'distanceToFood': -1
                }
        else:
            return {
                'numInvaders': -1000,
                'onDefense': 100,
                'invaderDistance': -10,
                'stop': -100,
                'reverse': -2
                }
