from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.util import counter
from pacai.core.directions import Directions
import random
import math


def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.agents.capture.dummy.DummyAgent',
        second = 'pacai.agents.capture.dummy.DummyAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    # firstAgent = reflection.qualifiedImport(first)
    # secondAgent = reflection.qualifiedImport(second)

    return [
        UngaBungaAgent(firstIndex),
        UngaBungaAgent(secondIndex),
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
        # takes a list of legal actions, and chooses the action that maximizes score
        # NEED TO CHANGE SO IF NEXT MOVE IS 'onDefense' WILL STOP THE AGENT FROM MOVING
        # OUTSIDE OF ITS GUARD ZONE
        # Collect legal moves.
        legalMoves = gameState.getLegalActions(self.index)
        # print("index: "+ str(self.index))
        # print("legalmoves"+ str(legalMoves))
        scores = {}
        bestActions = []

        # get scores and whether or not on offense or defense for each potential action
        for action in legalMoves:
            features = self.getFeatures(gameState, action)
            actionFeatures = 0
            #print(features['onDefense'])
            if features['onDefense'] == 1:
                #print("ondefense")
                actionFeatures = 1
            scores[action] = self.evaluate(gameState, action)
        # print(scores)
        if actionFeatures == 0 or actionFeatures == 1:
            currentMax = -math.inf
            for key in scores:
                if currentMax < scores[key]:
                    bestActions.clear()
                    currentMax = scores[key]
                if currentMax == scores[key]:
                    bestActions.append(key)

        #print(str(self.index) + str(bestActions))

        """
        # Choose one of the best actions.
        scores = [self.evaluate(gameState, action) for action in legalMoves]

        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best.
        # print(bestScore)
        """
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        #print(weights)
        #print(features)

        #print (features * weights)
        return features * weights

    def getFeatures(self, gameState, action):
        # Some helper variables that we may use during execution

        features = counter.Counter()
        successor = gameState.generateSuccessor(self.index, action)
        features['successorScore'] = self.getScore(successor)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        # check how many agents are on our team
        # split up team to Attackers(aSide) and Defenders(bSide) depending on size
        # half attack, half defense
        # default is offense so if only 1 agent, he's on offense
        features['onDefense'] = 0

        currentTeam = self.getTeam(gameState)
        teamLength = len(currentTeam)
        aSide = []
        bSide = []

        # this loop sets our agents to either a or b side depending on
        # the number of team members and this agent's index
        count = 1
        while count <= teamLength:
            if count % 2 == 0:
                bSide.append(currentTeam[count-1])
            else:
                aSide.append(currentTeam[count-1])
            count += 1

        if self.index in aSide:
            features['onDefense'] = 1
        else:
            features['onDefense'] = 1

        # % of our food vs their food
        ourFoodPosition = self.getFoodYouAreDefending(gameState)
        theirFoodPosition = self.getFood(gameState)
        ourFoodCount = 0
        theirFoodCount = 0

        # calculate size of map here as well
        layoutY = -2
        for foods in ourFoodPosition:
            layoutY += 1
            layoutX = -2
            for food in foods:
                layoutX += 1
                if str(food) == "True":
                    ourFoodCount += 1
        for foods in theirFoodPosition:
            for food in foods:
                if str(food) == "True":
                    theirFoodCount += 1

        ourFoodMoreOrEqual = ourFoodCount >= theirFoodCount

        # Add map layout X and Y so that we can tell what part of the map we're in
        # based on coordinates
        features['mapX'] = layoutX
        features['mapY'] = layoutY

        # Change features if on Offense:
        if features.get("onDefense") == 0:
            # print("on offense")
            # print(self.index)
            # Compute distance to the nearest food.
            foodList = self.getFood(successor).asList()

            # This should always be True, but better safe than sorry.
            if len(foodList) > 0:
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

            return features

        # Change features if on Defense
        elif features.get('onDefense') == 1:
            # print("on defense")
            # print(self.index)
            # Computes distance to invaders we can see.
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
            features['numInvaders'] = len(invaders)

            if myPos[0] > layoutX/2:
                features['inTeamSide'] = 1

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
                'invaderDistance': -100,
                'stop': -100,
                'reverse': -2,
                'inTeamSide': -1000
                }
