# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)

        return features

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """

    def closestGhost(self, pos, ghosts, walls):
        """
        closestGhost -- this is similar to the function that we have
        worked on in the search project; here its all in one place
        """
        fringe = [(pos[0], pos[1], 0)]
        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            # if we find a ghost at this location then exit
            if (pos_x, pos_y) in ghosts:
                return dist
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist+1))
        # no ghost found
        return None
    
    def getNearestGhost(self, pos, ghost, walls):
        """
        closestGhost -- this is similar to the function that we have
        worked on in the search project; here its all in one place
        """
        fringe = [(pos[0], pos[1], 0)]
        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            # if we find a ghost at this location then exit
            if ghost == (pos_x, pos_y):
                return dist
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist+1))
        # no ghost found
        return None

    def closestCapsule(self, pos, capsule, walls):
        """
        closestcapsule -- this is similar to the function that we have
        worked on in the search project; here its all in one place
        """
        fringe = [(pos[0], pos[1], 0)]
        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            # if we find a capsule at this location then exit
            if (pos_x, pos_y) in capsule:
                return dist
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist+1))
        # no capsule found
        return None

    def getTwoStepNeighbors(self, position, walls):
        x,y = position
        x_int, y_int = int(x + 1.5), int(y + 1.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    def getThreeStepNeighbors(self, position, walls):
        x,y = position
        x_int, y_int = int(x + 2.5), int(y + 2.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            try:
                dx, dy = vec
                next_x = x_int + dx
                if next_x < 0 or next_x == walls.width: continue
                next_y = y_int + dy
                if next_y < 0 or next_y == walls.height: continue
                if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
            except:
                pass
        return neighbors
        
    def getFourStepNeighbors(self, position, walls):
        x,y = position
        x_int, y_int = int(x + 3.5), int(y + 3.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            try:
                dx, dy = vec
                next_x = x_int + dx
                if next_x < 0 or next_x == walls.width: continue
                next_y = y_int + dy
                if next_y < 0 or next_y == walls.height: continue
                if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
            except:
                pass
        return neighbors

    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """
    def getFeatures(self, state, action):
        "*** YOUR CODE HERE ***"
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        ghost_states = state.getGhostStates()

        features = util.Counter()
        # to properly scale the function values independently of the features
        features["bias"] = 2.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        for g in ghost_states:
            # count the number of dangerous ghosts 1-step away
            if g.scaredTimer <= 1 and (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
                features["#-of-ghosts-1-step-away"] += 1.0
            # count the number of dangerous ghosts 2-step away
            elif g.scaredTimer <= 2 and (next_x, next_y) in self.getTwoStepNeighbors(g.getPosition(), walls):
                features["#-of-ghosts-2-step-away"] += 1.0
            elif g.scaredTimer <= 3 and (next_x, next_y) in self.getThreeStepNeighbors(g.getPosition(), walls):
                features["#-of-ghosts-3-step-away"] += 1.0
            # elif g.scaredTimer <= 4 and (next_x, next_y) in self.getFourStepNeighbors(g.getPosition(), walls):
            #     features["#-of-ghosts-4-step-away"] += 1.0


        # check if all ghosts are scared for at least 2-time-step
        all_ghosts_scared = all(ghost_state.scaredTimer >= 1 for ghost_state in ghost_states)
            

        for g in ghost_states:
            dist = self.getNearestGhost((next_x, next_y), g.getPosition(), walls)
            if dist is not None:
                # make the distance a number less than one otherwise the update
                # will diverge wildly
                features["min-dist-active-ghost"] = float(dist) / (walls.width * walls.height)
                
            if all_ghosts_scared:
                features["very-safe"] = 1.0
                dist = self.getNearestGhost((next_x, next_y), g.getPosition(), walls)
                if dist is not None:
                    # make the distance a number less than one otherwise the update
                    # will diverge wildly
                    features["min-dist-scared-ghost"] = float(dist) / (walls.width * walls.height)
                
            # if scared ghost is in pacman's range, eat it
            if g.scaredTimer >= 1 and (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
                features["#-of-scared-ghosts-1-step-away"] = 1.0
                features["fearless"] = 1.0
            # chase the scared ghost if the ghost is in pacman's range
            elif g.scaredTimer >= 2 and (next_x, next_y) in self.getTwoStepNeighbors(g.getPosition(), walls):
                features["#-of-scared-ghosts-2-step-away"] = 1.0
                features["fearless"] = 1.0
            # chase the scared ghost if the ghost is in pacman's range
            # elif g.scaredTimer >= 3 and (next_x, next_y) in self.getThreeStepNeighbors(g.getPosition(), walls):
            #     features["#-of-scared-ghosts-3-step-away"] = 1.0
            #     features["fearless"] = 1.0
            # elif g.scaredTimer >= 4 and (next_x, next_y) in self.getFourStepNeighbors(g.getPosition(), walls):
            #     features["#-of-scared-ghosts-4-step-away"] += 1.0
            #     features["fearless"] = 1.0
            else:
                features["get-capsule"] = 1
        
        
        capsule_dist = self.closestCapsule((next_x, next_y), state.getCapsules(), walls)
        if capsule_dist is not None:
            features["min-dist-capsule"] = float(capsule_dist) / (walls.width * walls.height)
                

        # if there is no danger of ghosts then add the food feature
        if ((not features["#-of-ghosts-1-step-away"] 
            or not features["#-of-ghosts-2-step-away"] 
            or all_ghosts_scared) and food[next_x][next_y] 
            and features["fearless"] != 0):
            features["eats-food"] = 1.0
        
        if len(state.getLegalActions(0)) >= 4:
            # is pacman free to move?
            features["free-to-move"] = len(state.getLegalActions(0))

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(5.0)
        return features
    

# python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic