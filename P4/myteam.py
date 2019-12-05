
# from pacai.util import reflection
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

    # have to call the class since using qualified import wouldn't work in the server
    return [
        UngaBungaAgent(firstIndex),
        UngaBungaAgent(secondIndex),
    ]


class UngaBungaAgent(CaptureAgent):

    # initializes Our Ungabunga agent, nothing to fancy, don't have to make any changes to init
    def __init__(self, index, **kwargs):
        super().__init__(index)
        self.lava_floor = 0

    # takes a list of legal actions, and chooses the action that maximizes score based on the
    # current features the agent has. Scores are calculated by multiplying features by weights
    # and then summing them together. The highest score is chosen as the action, if two scores
    # are equal, then we randomly choose one
    def chooseAction(self, gameState):

        """
        Evaluates potential actions and returns a value
        """
        # INITIALIZING VARIABLES:
        # legal moves - takes all the available moves
        # scores - a dictionary that keeps track of our scores
        # bestActions - a list that keeps track of the highest scoring actions
        # takes all the available legal moves
        legalMoves = gameState.getLegalActions(self.index)
        scores = {}
        bestActions = []

        # ALGORITHM GOAL: to loop through available actions and evaluate the actions value
        # IMPLEMENTATION: Calls our list of legalMoves and iterates through each action. Each
        # action is then assigned to our scores dictionary with its given value.
        # VARIABLES USED:
        # action - holds the current action as we iterate through legalMoves
        # legalMoves - a list of all available moves
        # scores - a dictionary that keeps track of scores
        # FUNCTIONS CALLED:
        # self.evaluate - takes a given state and action and evaluates their value using
        # weights and features
        for action in legalMoves:
            scores[action] = self.evaluate(gameState, action)

        # ALGORITHM GOAL: to check which action(s) in the dictionary has the highest value(s)
        # IMPLEMENTATION: Calls our dictionary of scores and iterates through each key. We
        # initially have a variable called currentMax that is assigned to -infinity. This
        # variable ensures no matter how low in value an action is, it's still going into the
        # list of bestActions so we always have at least one action. As we iterate through
        # each key, we check if the key's value is higher then our currentMax value - if it is
        # then we clear our list of bestActions and assign this key as our currentMax. An edge
        # case is that two or more keys have the same value - if this happens, then we do NOT
        # clear our list of bestActions
        # VARIABLES USED:
        # currentMax - integer that is originally set to -infinity
        # bestActions - a list of actions
        # key - holds the current key as we iterate through scores
        currentMax = -math.inf
        for key in scores:
            if currentMax < scores[key]:
                bestActions.clear()
                currentMax = scores[key]
            if currentMax == scores[key]:
                bestActions.append(key)

        # RETURNED: Now that we have a list of bestActions available, we return it to our
        # agent. We use random.choice so that if the list has more than one available best
        # action, we choose one randomly as a tiebreaker
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """
        # INITIALIZING VARIABLES:
        # features - a dictionary that holds our features given an action
        # weights - a dictionary that holds our weights per feature
        # FUNCTIONS CALLED:
        # self.getFeatures - returns a dictionary of features given a state and action
        # self.getWeights - returns a dictionary of weights given a state and action
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)

        # RETURNED: Now that we have our features and weights we multiply them and add them
        # together to return a value. When you multiply two dictionaries together, we multiply
        # the values in similar keys. EX: if key 'onDefense' is in features AND in
        # weights, then their values are multiplied. These multiplied values are then summed
        # together and returned.
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Given an agent, their successor actions, and potential conditions fulfilled, returns
        a dictionary of features.
        """
        # INITIALIZING VARIABLES:
        # features - a dictionary that holds our features given an action, originally
        # initialized with zero's
        # successor - returns a state given an agent and action
        # myState - an agents state given a successor state
        # myPos - an agents coordinates in (x,y) format for that successor state
        # features['onDefense] - tells the agent whether they are playing offense (0) or
        # playing defense (1), defaults to offense so that we always have at least one attacker
        # currentTeam - a list of agents (and their indexes) on our agent's team
        # aSide - a list of agents that will be playing offense (0)
        # bSide - a list of agents that will be playing defense (1)
        features = counter.Counter()
        successor = gameState.generateSuccessor(self.index, action)
        features['successorScore'] = self.getScore(successor)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        features['onDefense'] = 0
        currentTeam = self.getTeam(gameState)

        aSide = []
        bSide = []

        # ALGORITHM GOAL: to assign each agent on the team to either offense or defense
        # IMPLEMENTATION: creates a while loop that iterates through our team. Count keeps
        # track of which agent in the team list we're on. Since our indexes for each agent
        # will be varying numbers, we keep track of their placement on the team to assign
        # them to offense or defense. The first agent in the currentTeam list is assigned
        # to offense, next player to defense and so on. We use a modulo to check if which
        # index they're in to keep track of players being sent to offense or defense. After
        # being added to either aSide or bSide, the features of the agent are updated.
        # VARIABLES USED:
        # count - integer that will keep track of which index the agent is on
        # teamLength - length of the team
        # bSide - our list of defense agents
        # aSide - our list of offense agents
        count = 1
        while count <= len(currentTeam):
            if count % 2 == 0:
                bSide.append(currentTeam[count - 1])
            else:
                aSide.append(currentTeam[count - 1])
            count += 1

        if self.index in aSide:
            features['onDefense'] = 0
        else:
            features['onDefense'] = 1

        # ALGORITHM GOAL: to create a variable that keeps track of our teams food vs their team
        # and to get the X and Y values of the entire map
        # IMPLEMENTATION: initializes the food positions - since each bit of the map either has
        # food or doesn't, we can use the x and y values to create a layout. We create a for
        # loop that will iterate through our foodPosition, incrementing X for each x value,
        # and incrementing y for each y value. Since our foodlist is actually a grid, we can
        # find the X by the length of each row so we just increase x by 1 for each row(foods)
        # We then find Y by the number of rows so we increase y for each row iterated.
        # VARIABLES USED:
        # ourFoodPosition - a grid of all our food positions
        # foods - holds the current food as we iterate through ourFoodPosition
        # theirFoodPosition - a grid of all of our enemy's food positions
        # ourFoodCount - an integer that keeps track of amount of our food at each state
        # theirFoodCount - an integer that keeps track of amount of enemy food at each state
        # layoutX - keeps track of largest X in map, initially set to -2 since each layout
        # has an x on each side that is unreachable by all agents/food
        # layoutY - keeps track of largest Y in map, initially set to -2 since each layout
        # has an y on each side that is unreachable by all agents/food
        # ourFoodMore or Equal - a boolean that returns whether or not we have more food than
        # the opposing team
        ourFoodPosition = self.getFoodYouAreDefending(gameState)
        theirFoodPosition = self.getFood(gameState)
        ourFoodCount = 0
        theirFoodCount = 0
        layoutX = -2

        capsule = self.getCapsulesYouAreDefending(gameState)
        if len(capsule) == 0:
            features['onDefense'] = 0

        for foods in ourFoodPosition:
            layoutX += 1
            layoutY = -2
            for food in foods:
                layoutY += 1
                if str(food) == "True":
                    ourFoodCount += 1

        for foods in theirFoodPosition:
            for food in foods:
                if str(food) == "True":
                    theirFoodCount += 1

        # CURRENTLY NOT BEING USED
        # ourFoodMoreOrEqual = ourFoodCount >= theirFoodCount

        # Add map layout X and Y so that we can tell what part of the map we're in
        # based on coordinates
        features['mapX'] = layoutX
        features['mapY'] = layoutY

        # *************************************
        # VERY IMPORTANT TO HOW OUR AGENTS WORK
        # *************************************
        # This entire section is dedicated to how our agents assign features and weights based
        # on situations that they may encounter during each game. It is divided into two
        # sections, one for Offense (0) and the other for Defense (1). Each section will
        # initiate ONLY THE FEATURES IT NEEDS.

        # Change features if on Offense:
        


        if features.get("onDefense") == 0:

            #compute distance from DangerousEnemies
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            DangerEnemies = [a for a in enemies if a.isGhost() and a.getPosition() is not None]
            
            if len(DangerEnemies) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in DangerEnemies]
                features['DangerousEnemyDistance'] = sum(dists)/len(dists)
                features['closestEnemy'] = min(dists)

            # Compute distance to the nearest food.
            foodList = self.getFood(successor).asList()            

            if len(foodList) > 0:
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

            # Compute distance to nearest Capsule
            capsules = self.getCapsules(successor)

            if len(capsules) > 0:
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, big_fruit) for big_fruit in capsules])
                features['distanceToCapsule'] = minDistance

            for food1 in foodList:
                for food2 in foodList:
                    ClusterDist = self.getMazeDistance(food1, food2)
                    if ClusterDist < 3: features['foodCluster'] = ClusterDist

            


            # Check if agent is still on our side of the map AND if we currently have an
            # invader, if yes, then head straight for the invader. Divided into two "if"
            # statements to check if we're blue or red
            if self.red:
                if myPos[0] <= layoutX / 2:
                    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                    invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]

                    features['numInvaders'] = len(invaders)

                    
                    self.lava_floor += 1
                    features['ourFloorIsLava'] = self.lava_floor

                    if len(invaders) > 0:
                        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                        features['invaderDistance'] = min(dists)
                else:
                    #this is so we dont want to stay on this side of the map
                    self.lava_floor = 0


            else:
                if myPos[0] >= layoutX / 2:

                    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                    invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]

                    features['numInvaders'] = len(invaders)

                    self.lava_floor += 1
                    features['ourFloorIsLava'] = self.lava_floor

                    if len(invaders) > 0:
                        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                        features['invaderDistance'] = sum(dists)/len(dists)
                else:
                    self.lava_floor = 0
                   

            return features

        # Change features if on Defense
        elif features.get('onDefense') == 1:

            # Computes distance to invaders and potential invaders. Invaders being agents that
            # have entered our area, and potential invaders being all enemy agents that are
            # not currently in our area.
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
            potentialInvaders = [a for a in enemies if a.isGhost() and a.getPosition() is not None]

            # assigns the number of invaders and potential invaders to our features
            features['numInvaders'] = len(invaders)
            features['numPotentialInvaders'] = len(potentialInvaders)

            # prioritizes our features so that we stay on our side of the map. Our agent seems
            # to do much better if they believe the line of scrimmage is one space away so
            # the distances are adjusted for it (this usually means the enemy is baited into
            # our territory)
            if self.red:
                if myPos[0] <= (layoutX / 2) - 1:
                    features['inTeamSide'] = 1
                    # features['inEnemySide'] = 0
            else:
                if myPos[0] >= (layoutX / 2) + 2:
                    features['inTeamSide'] = 1
                    # features['inEnemySide'] = 0

            # If our agent is currently a scared ghost, then we will kamikaze the enemy so
            # that we respawn as fast as we can.
            if myState.isScaredGhost():
                features['witnessMEEEE'] = 1

            # If we have invaders, we prioritize minimizing the distance between our agent and
            # the invader. THIS TAKES THE HIGHEST PRIORITY AS A DEFENDER
            if len(invaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)

            # if we there are enemies on their own side of the map, we prioritize minimizing
            # the distance between our agent and potential threats
            if len(potentialInvaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in potentialInvaders]
                features['potentialInvaderDistance'] = min(dists)

            # If stop is a potential action, we initialize it as a feature so that we can
            # prioritize our agent NOT to stop (stopping usually leads to stalemates and
            # negative interactions)
            if action == Directions.STOP:
                features['stop'] = 1

            # Honestly, I don't know what this does, but it was in the capture agent code
            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if action == rev:
                features['reverse'] = 1

            return features

    def getWeights(self, gameState, action):
        """
        Returns a dict of weights for the state.
        The keys match up with the return from `ReflexCaptureAgent.getFeatures`.
        """
        # MINIMIZING DISTANCES:
        # the following features are distances that we minimize so a HIGHER NEGATIVE
        # VALUE CREATES A HIGHER PRIORITY:
        # distanceToFood
        # numInvaders
        # invaderDistance
        # witnessMEEEE
        # REST OF WEIGHTS:
        # The rest of the weights prioritize higher values
        # EX: inTeamSide: 150 - as a defender, staying in team side is worth more points than
        # going into enemy territory
        features = self.getFeatures(gameState, action)
        if features['onDefense'] == 0:
            return {'successorScore': 100, 'distanceToFood': -5, 'numInvaders': -1500,
                    'invaderDistance': -500, 'distanceToCapsule':-2, 'DangerousEnemyDistance': 1,
                    'ourFloorIsLava': -1, 'closestEnemy':2, 'foodCluster': -2}
        else:
            return {'numInvaders': -1500, 'onDefense': 100, 'invaderDistance': -500,
                    'potentialInvaderDistance': -5, 'stop': -100, 'reverse': -10,
                    'inTeamSide': 150, 'witnessMEEEE': -1250}
