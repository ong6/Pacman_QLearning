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

    def closestGhost(self, pos, ghost, walls):
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

        features = util.Counter()
        # to properly scale the function values independently of the features
        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)


        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)


        # check if all ghosts are scared
        ghost_states = state.getGhostStates()
        ghosts_scared = all(ghost_state.scaredTimer != 0 for ghost_state in ghost_states)
        if ghosts_scared:
            features["ghosts-scared"] = 1.0

        # if there is no danger of ghosts then add the food feature
        if (not features["#-of-ghosts-1-step-away"] or ghosts_scared) and food[next_x][next_y]:
            features["eats-food"] = 1.0

        # if scared, check if pacman is in a ghost's scared range
        if ghosts_scared:
            for g in state.getGhostStates():
                if g.scaredTimer !=0 and (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
                    features["#-of-scared-ghosts-1-step-away"] += 1.0
                    features["eats-ghost"] = 1.0
                    dist = self.closestGhost((next_x, next_y), g.getPosition(), walls)
                    if dist is not None:
                        # make the distance a number less than one otherwise the update
                        # will diverge wildly
                        features["closest-ghost"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features
    
class NewExtractor2(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """

    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """
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
    
    def closestGhost(self, pos, ghost, walls):
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
        
        # count the number of ghosts 2-step away
        features["#-of-ghosts-2-step-away"] = sum((next_x, next_y) in self.getTwoStepNeighbors(g, walls) for g in ghosts)


        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
            
        # check if all ghosts are scared
        ghost_states = state.getGhostStates()
        all_ghosts_scared = all(ghost_state.scaredTimer >= 2 for ghost_state in ghost_states)
        some_ghosts_scared = any(ghost_state.scaredTimer >= 2 for ghost_state in ghost_states)
        
            
        # if scared, check if pacman is in a ghost's scared range
        if some_ghosts_scared:
            for g in ghost_states:
                if g.scaredTimer >= 2 and util.manhattanDistance((next_x, next_y), g.getPosition()) <= 5:
                    features["close-ghost"] += 2.0
                
                if g.scaredTimer >= 2 and (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
                    features["#-of-scared-ghosts-1-step-away"] += 1.0
                    dist = self.closestGhost((next_x, next_y), g.getPosition(), walls)
                    if dist is not None:
                        # make the distance a number less than one otherwise the update
                        # will diverge wildly
                        features["closest-safe-ghost"] = float(dist) / (walls.width * walls.height)
        else: 
            for g in ghost_states:
                dist = self.closestGhost((next_x, next_y), g.getPosition(), walls)
                if dist is not None:
                    # make the distance a number less than one otherwise the update
                    # will diverge wildly
                    features["closest-danger-ghost"] = float(dist) / (walls.width * walls.height)
            
            
        # if there is no danger of ghosts then add the food feature
        if (not features["#-of-ghosts-1-step-away"] and not features["#-of-ghosts-2-step-away"] or all_ghosts_scared) and food[next_x][next_y]:
            features["eats-food"] = 2.0
            
        features.divideAll(9.0)
        return features

    
    
# python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic
# python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q