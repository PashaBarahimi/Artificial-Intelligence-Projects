import random
from dataclasses import dataclass
from timeit import default_timer as timer

CROSSOVER_PROBABILITY = 0.8
MUTATION_PROBABILITY = 0.05
CARRY_PERCENTAGE = 0.2
POPULATION_SIZE = 100
MULTI_START_COUNT = 10

OPERATOR_PRECEDENCE = {
    '+': 1,
    '-': 1,
    '%': 2,
    '*': 2
}

OPERATOR_FUNCTION = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '%': lambda x, y: x % y,
    '*': lambda x, y: x * y
}


@dataclass
class EquationBuilder:
    operators: list[str]
    operands: list[int]
    equationLength: int
    goalNumber: int
    population: list[list]

    def __init__(self, operators: list[str], operands: list[int], equationLength: int, goalNumber: int, maxGenCount: int):
        self.operators = operators
        self.operands = operands
        self.equationLength = equationLength
        self.goalNumber = goalNumber
        self.maxGenCount = maxGenCount

    def makeFirstPopulation(self) -> list[list]:
        operandCount = int(self.equationLength / 2) + 1
        operatorCount = int(self.equationLength / 2)

        population = []
        for _ in range(POPULATION_SIZE):
            chromosome = [0] * self.equationLength
            for j in range(operandCount):
                chromosome[j * 2] = random.choice(self.operands)
            for j in range(operatorCount):
                chromosome[j * 2 + 1] = random.choice(self.operators)  # type: ignore
            population.append(chromosome)
        return population

    def findEquation(self, multiStartCount: int = 1) -> tuple[list, bool]:
        bestSolution = None
        for _ in range(multiStartCount):
            self.population = self.makeFirstPopulation()
            for _ in range(self.maxGenCount):
                random.shuffle(self.population)

                fitnesses = [self.calcFitness(self.population[i]) for i in range(POPULATION_SIZE)]
                if max(fitnesses) == 1:
                    return self.population[fitnesses.index(1)], True

                bestChromosomes = [x for _, x in sorted(zip(fitnesses, self.population), key=lambda pair: pair[0], reverse=True)]
                if bestSolution is None or self.calcFitness(bestSolution) < self.calcFitness(bestChromosomes[0]):
                    bestSolution = bestChromosomes[0]
                carriedChromosomes = []
                for i in range(0, int(POPULATION_SIZE * CARRY_PERCENTAGE)):
                    carriedChromosomes.append(bestChromosomes[i])

                matingPool = self.createMatingPool(bestChromosomes)
                crossoverPool = self.createCrossoverPool(matingPool)
                self.population.clear()

                for i in range(POPULATION_SIZE - int(POPULATION_SIZE * CARRY_PERCENTAGE)):
                    self.population.append(self.mutate(crossoverPool[i]))

                self.population.extend(carriedChromosomes)

        return bestSolution, False # type: ignore

    def createMatingPool(self, bestChromosomes: list[list]) -> list[list]:
        ranks = list(reversed(range(1, POPULATION_SIZE + 1)))
        matingPool = []
        for i in range(POPULATION_SIZE):
            for _ in range(ranks[i]):
                matingPool.append(bestChromosomes[i])
        random.shuffle(matingPool)
        return matingPool[:POPULATION_SIZE]

    def createCrossoverPool(self, matingPool: list[list]) -> list[list]:
        crossoverPool = []
        for i in range(0, len(matingPool) - 1, 2):
            if random.random() > CROSSOVER_PROBABILITY:
                crossoverPool.append(matingPool[i])
                crossoverPool.append(matingPool[i + 1])
            else:
                children = self.crossover(matingPool[i], matingPool[i + 1])
                crossoverPool.extend(children)
        return crossoverPool

    def crossover(self, chromosome1: list, chromosome2: list) -> tuple[list, list]:
        crossoverPoint1 = random.randint(0, self.equationLength - 1)
        crossoverPoint2 = random.randint(0, self.equationLength - 1)
        if crossoverPoint1 > crossoverPoint2:
            crossoverPoint1, crossoverPoint2 = crossoverPoint2, crossoverPoint1

        chromosome1 = list(chromosome1)
        chromosome2 = list(chromosome2)
        for i in range(crossoverPoint1, crossoverPoint2):
            chromosome1[i], chromosome2[i] = chromosome2[i], chromosome1[i]

        return chromosome1, chromosome2

    def mutate(self, chromosome: list) -> list:
        chromosome = list(chromosome)
        for i in range(len(chromosome)):
            if random.random() < MUTATION_PROBABILITY:
                if chromosome[i] in self.operators:
                    chromosome[i] = random.choice(self.operators)
                else:
                    chromosome[i] = random.choice(self.operands)
        return chromosome

    def calcFitness(self, chromosome: list) -> float:
        return 1 / (abs(self.goalNumber - eval("".join(map(str, chromosome)))) + 1)


def getBuildTime(equationBuilder: EquationBuilder, testCount: int) -> float:
    buildTimes = []
    for _ in range(testCount):
        start = timer()
        equationBuilder.findEquation()
        end = timer()
        buildTimes.append(end - start)
    return sum(buildTimes) / len(buildTimes)


def main():
    operands = [1, 2, 3, 4, 5, 6, 7, 8]
    operators = ['+', '-', '*']
    equationLength = 21
    goalNumber = 18019

    equationBuilder = EquationBuilder(operators, operands, equationLength, goalNumber, equationLength * POPULATION_SIZE * 2)
    equation, isFound = equationBuilder.findEquation(MULTI_START_COUNT)
    if not isFound:
        print("No equation found! Best solution:")
    print(*equation, "=", eval("".join(map(str, equation))))
    print(f"Average Build Time: {getBuildTime(equationBuilder, 10):.4f}s")


if __name__ == "__main__":
    main()
