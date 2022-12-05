inputFile = 'data/input5.txt'
answer = [28, 30, 9, 24, 11, 3, 13, 23, 28, 22, 5, 7, 29]
cost = 12


class Graph:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.current = 0
        self.parent = None
        self.adj = [set() for _ in range(n)]
        self.difficulties = {}
        self.requirements = {}
        self.remainingTime = 0


def readInput(path):
    with open(path, 'r', encoding='utf-8') as f:
        n, m = map(int, f.readline().split())
        graph = Graph(n, m)
        for _ in range(m):
            u, v = map(int, f.readline().split())
            graph.adj[u - 1].add(v - 1)
            graph.adj[v - 1].add(u - 1)
        h = int(f.readline())
        for _ in range(h):
            u = int(f.readline()) - 1
            graph.difficulties[u] = -1
        s = int(f.readline())
        for _ in range(s):
            inp = f.readline().split()
            p = int(inp[0]) - 1
            vertices = {int(x) - 1 for x in inp[2:]}
            graph.requirements[p] = vertices
        i = int(f.readline()) - 1
        graph.current = i
    return graph


g = readInput(inputFile)

answer = [x - 1 for x in answer]

if g.current != answer[0]:
    print('Wrong starting vertex')
    exit(1)

for i in range(len(answer) - 1):
    if answer[i + 1] not in g.adj[answer[i]]:
        print('Wrong path')
        exit(1)

additional = 0
for d in g.difficulties:
    if answer.count(d) > 0:
        additional += answer.count(d) - 1

if cost != len(answer) + additional - 1:
    print('Wrong cost')
    exit(1)

for u in answer:
    for r, vertices in g.requirements.items():
        if u in vertices:
            vertices.remove(u)
    if u in g.requirements and len(g.requirements[u]) == 0:
        g.requirements.pop(u)

if len(g.requirements) > 0:
    print('Wrong requirements')
    exit(1)

print('Correct')
