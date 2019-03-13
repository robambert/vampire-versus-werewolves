from Tray import Tray
import numpy as np
import concurrent.futures
import sys

class Node():
    def __init__(self, tray):
        self.tray = tray
        self.children = []
        self.edges = []

    def Expand(self, maxSplit):
        if self.children == []:
            #self.edges = self.tray.GetChildren(maxSplit)[1:]
            self.edges = self.tray.GetEdges(maxSplit)[1:]
            for edge in self.edges:
                newTray = Tray(self.tray.N, self.tray.M, [], Type = self.tray.Type)
                newTray.Grid = np.copy(self.tray.Grid)
                newTray.UpdateLists()
                newTray.UpdateTray(edge, is_upd = False)
                newTray.Type = 5 - newTray.Type
                self.children.append(Node(newTray))
    
    def GetDepth(self):
        d = 0
        node = self
        while True:
            try:
                node = node.children[0]
                d += 1
            except:
                return d

def AlphaBeta(node : Node, d : int, maxSplit : int, gamma = 0.8):
    node.Expand(maxSplit)
    moves : list
    maxv = -float('inf')
    res : Node
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(MinValue, child, -float('inf'), float('inf'), d - 1, maxSplit, gamma) : k for k, child in enumerate(node.children)}
        for future in concurrent.futures.as_completed(futures):
            k = futures[future]
            child, v = future.result()
            if v >= maxv:
                maxv = v
                moves = node.edges[k]
                res = child
    """
    for k, child in enumerate(node.children):
        c, v = MinValue(child, -float('inf'), float('inf'), d - 1, maxSplit, gamma)
        if v >= maxv:
            maxv = v
            moves = node.edges[k]
            res = c
    """
    mov = []
    for move in moves:
        if not(move[0]==move[3] and move[1]==move[4]):
            mov += move
    return res, ["MOV", int(len(mov)/5), mov]


def MaxValue(node : Node, alpha : float, beta : float, d : int, maxSplit : int, gamma = 0.8):
    if node.tray.IsTerminal():
        if node.tray.Win():
            return node, 1000000
        else:
            return node, -1000000
    elif d==0:
        return node, node.tray.Heuristic(1) 
    v = -float('inf')
    node.Expand(maxSplit)
    for k, child in enumerate(node.children):
        c, newv = MinValue(child, alpha, beta, d - 1, maxSplit, gamma)
        v = gamma*max(v, newv)
        node.children[k] = c
        if v >= beta:
            node.children = node.children[:k+1]
            return node, v
        alpha = max(alpha, v)
    return node, v

def MinValue(node : Node, alpha : float, beta : float, d : int, maxSplit : int, gamma = 0.8):
    if node.tray.IsTerminal():
        if node.tray.Win():
            return node, -1000000
        else:
            return node, 1000000
    elif d == 0:
        return node, node.tray.Heuristic(-1)
    v = float('inf')
    node.Expand(maxSplit)
    sameTray = Tray(node.tray.N, node.tray.M, [], Type = 5-node.tray.Type)
    sameTray.Grid = np.copy(node.tray.Grid)
    sameTray.UpdateLists()
    print([child.tray.Vampires for child in node.children])
    node.children = [Node(sameTray)]+node.children
    print([child.tray.Vampires for child in node.children])
    for k, child in enumerate(node.children):
        c, newv = MaxValue(child, alpha, beta, d - 1, maxSplit, gamma)
        v = gamma * min(v, newv)
        node.children[k] = c
        if v <= alpha:
            node.children = node.children[:k+1]
            return node, v
        beta = min(beta, v)
    return node, v