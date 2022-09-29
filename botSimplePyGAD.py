from sc2 import maps, score
from sc2.bot_ai import BotAI  
from sc2.data import Difficulty, Race, Result
from sc2.main import run_game  
from sc2.player import Bot, Computer  
from sc2.position import Point2
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId

import random
import time

import pygad
import numpy


class simpleBot(BotAI):

    def on_end(self, game_result):

        inputs = [totalWorkers, totalBarracks, totalMarines, 25]
        def fitness_func(solution, solution_idx):
            T_max = 3600
            T_partida = self.time
            T_puntos = T_max - T_partida
            out = numpy.sum(numpy.abs(inputs-solution))

            fitness = T_puntos + 100/out

            if T_partida > T_max:
                print("Tiempo máximo de partida superado, resultados no concluyentes")
                fitness = -99999

            else:
                if game_result == Result.Victory:
                    fitness

                else:
                    fitness = -fitness

            return fitness

        ga_instance = pygad.GA(num_generations=1000,
            sol_per_pop=100,
            num_parents_mating=10,
            num_genes=4,
            fitness_func=fitness_func,
            gene_type = int,
            init_range_low = 1,
            init_range_high = 75,
            random_mutation_min_val = 1.0,
            random_mutation_max_val = 10.0,
            mutation_by_replacement = True,
            save_best_solutions = True,
            save_solutions = True,
            suppress_warnings = True)

        ga_instance.run()
        ga_instance.plot_fitness()
        ga_instance.plot_genes()
        ga_instance.plot_new_solution_rate()
        solution, solution_fitness, solution_idx = ga_instance.best_solution()

        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - BEST SOLUTION AFTER - - - - - -')
        print('Generation 1  ',ga_instance.best_solutions[0])
        print('Generation 345',ga_instance.best_solutions[344])
        print('Generation 981',ga_instance.best_solutions[980])
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - BEST SOLUTION - - - - - - - -')
        print("Solution: {solution}".format(solution = solution))
        print("Fitness value: {solution_fitness}".format(solution_fitness = solution_fitness))
        print("Solution index: {solution_idx}".format(solution_idx = solution_idx))
        

        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - GAME STATS - - - - - - - - - -')
        print(game_result, ' |  Total time:', self.time)
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - OWN STATS - - - - - - - - - -')
        print('Minerals:',self.state.score.summary[8][1], ' |  Gas:',self.state.score.summary[9][1], ' |  Supply:',self.supply_used,'/',self.supply_cap)
        print('Total units:',totalWorkers+totalMarines, ' |  Defeated units:',totalWorkers+totalMarines-self.units.amount, ' |  Structures:',totalSD+totalRefinery+totalBarracks+self.structures(UnitTypeId.COMMANDCENTER).amount)
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - ENEMY STATS - - - - - - - - -')
        print('Total units:',max(totalEnemyUnits), ' |  Defeated units:',max(totalEnemyUnits)-self.enemy_units.amount, ' |  Structures:',max(totalEnemyStructures))
    
   
    async def on_start(self):
        
        scout = self.workers[0]                         #scout inicial
        scout.attack(self.enemy_start_locations[0])

        global totalEnemyUnits 
        totalEnemyUnits = []

        global totalEnemyStructures
        totalEnemyStructures = []

    
    async def on_step(self,iteration):

        print('iteration:',iteration)
        
        await self.distribute_workers()         #distribución de obreros para recolectar

        await self.train_workers(iteration)     #creación de obreros

        await self.count_enemy_units()          #cuenta unidades enemigas totales

        await self.count_enemy_structures()     #cuenta estructuras enemigas totales

        await self.expand()                     #construcción nuevo centro de mando

        await self.build_supply_depot(iteration)         #construcción dep suministros

        await self.build_refinery(iteration)             #construcción refinerías

        await self.build_barrack(iteration)              #construcción barracones

        await self.train_marines(iteration)              #creación marines

        await self.attack()                              #ataque


    
    async def train_workers(self,iteration):
        if iteration == 0:
            global totalWorkers
            totalWorkers = self.units.amount

        for command_center in self.structures(UnitTypeId.COMMANDCENTER).ready: 
            if self.units(UnitTypeId.SCV).amount < 22 * self.structures(UnitTypeId.COMMANDCENTER).amount and command_center.is_idle and self.can_afford(UnitTypeId.SCV):
                command_center.train(UnitTypeId.SCV)
                totalWorkers += 1                                                 #cuenta trabajadores propios totales  
            
    
    async def count_enemy_units(self):
        if self.enemy_units:
            totalEnemyUnits.append(self.enemy_units.amount)


    async def count_enemy_structures(self):
        if self.enemy_structures:
            totalEnemyStructures.append(self.enemy_structures.amount)

    
    async def expand(self):
        if self.structures(UnitTypeId.COMMANDCENTER).amount < 2 and self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.expand_now()

        elif self.structures(UnitTypeId.COMMANDCENTER).amount < 3 and self.supply_used > 50 and self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.expand_now()


    async def build_supply_depot(self, iteration):
        if iteration == 0:
            global totalSD
            totalSD = self.structures(UnitTypeId.SUPPLYDEPOT).amount

        for command_center in self.structures(UnitTypeId.COMMANDCENTER).ready: 
            if self.supply_left < 5 and self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 2:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=command_center.position.towards(self.game_info.map_center, 10))
                totalSD += 1
                            

    async def build_refinery(self, iteration):
        if iteration == 0:
            global totalRefinery
            totalRefinery = self.structures(UnitTypeId.REFINERY).amount

        elif self.structures(UnitTypeId.REFINERY).amount < 2 * self.structures(UnitTypeId.COMMANDCENTER).ready.amount:
            for command_center in self.structures(UnitTypeId.COMMANDCENTER).ready:
                gases = self.vespene_geyser.closer_than(10, command_center)
                for gas in gases:
                    if self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.REFINERY):
                        await self.build(UnitTypeId.REFINERY, gas)
                        totalRefinery += 1


    async def build_barrack(self, iteration):
        if iteration == 0:
            global totalBarracks
            totalBarracks = self.structures(UnitTypeId.BARRACKS).amount

        elif self.structures(UnitTypeId.SUPPLYDEPOT):
            for command_center in self.structures(UnitTypeId.COMMANDCENTER):
                if self.structures(UnitTypeId.BARRACKS).amount < 3 * self.structures(UnitTypeId.COMMANDCENTER).ready.amount and self.can_afford(UnitTypeId.BARRACKS) and self.already_pending(UnitTypeId.BARRACKS) < 2:
                    await self.build(UnitTypeId.BARRACKS, near=command_center.position.towards(self.game_info.map_center, 15))
                    totalBarracks += 1
        

    async def train_marines(self, iteration):
        if iteration == 0:
            global totalMarines
            totalMarines = self.units(UnitTypeId.MARINE).amount

        for barrack in self.structures(UnitTypeId.BARRACKS).ready:
            if self.units(UnitTypeId.MARINE).amount < 25 * self.structures(UnitTypeId.COMMANDCENTER).ready.amount and self.can_afford(UnitTypeId.MARINE) and not self.already_pending(UnitTypeId.MARINE):
                barrack.train(UnitTypeId.MARINE)
                totalMarines += 1


    async def attack(self):
        if self.units(UnitTypeId.MARINE).amount >= 25:
            for marine in self.units(UnitTypeId.MARINE).idle:

                if self.enemy_units:
                    marine.attack(random.choice(self.enemy_units))

                elif self.enemy_structures:
                    marine.attack(random.choice(self.enemy_structures))

                else:
                    marine.attack(self.enemy_start_locations[0].position)
        

run_game( 
    maps.get("LightshadeAIE"),                 #mapa en el que se juega
    [Bot(Race.Terran, simpleBot()),                    #raza de nuestro bot
     Computer(Race.Random, Difficulty.VeryEasy)],       #raza del enemigo y dificultad
     realtime=False                                #velocidad juego
)

