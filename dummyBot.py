from sc2 import maps, score
from sc2.bot_ai import BotAI  
from sc2.data import Difficulty, Race, Result
from sc2.main import run_game  
from sc2.player import Bot, Computer  
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId


import time

class dummyBot(BotAI):

    def on_end(self, game_result):
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - - GAME STATS - - - - - - - - -')
        print(game_result, ' |  Total time:', self.time)
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - - OWN STATS - - - - - - - - -')
        print('Minerals:',self.minerals, ' |  Gas:',self.vespene, ' |  Supply:',self.supply_used,'/',self.supply_cap)
        print('Total units:',totalWorkers, ' |  Defeated units:',totalWorkers-self.units.amount, ' |  Structures:',self.structures.amount)
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('- - - - - - - - - ENEMY STATS - - - - - - - - -')
        print('Total units:',totalEnemyUnits+12, ' |  Defeated units:',totalEnemyUnits-self.enemy_units.amount, ' |  Structures:',self.enemy_structures.amount)
    
    async def on_step(self,iteration):

        print('iteration:',iteration)
        

        await self.distribute_workers()         #distribución de obreros para recolectar

        await self.train_workers(iteration)     #creación de obreros

        await self.initial_scout(iteration)     #scout inicial

        await self.count_enemy_units()          #cuenta unidades enemigas totales


    async def train_workers(self,iteration):
        if iteration == 0:
            global totalWorkers
            totalWorkers = self.units.amount

        for command_center in self.structures(UnitTypeId.COMMANDCENTER).ready: 
            if command_center.is_idle and self.can_afford(UnitTypeId.SCV):      #se crean obreros siempre que se pueda
                command_center.train(UnitTypeId.SCV)
                totalWorkers += 1                                                 #cuenta trabajadores propios totales  
                
    
    async def initial_scout(self, iteration):
        if iteration == 0:                            #mandar a un scout al empezar
            scout = self.workers[0]
            scout.attack(self.enemy_start_locations[0])
            
    
    async def count_enemy_units(self):
        global totalEnemyUnits                  
        totalEnemyUnits = 0
        for eunit in self.enemy_units:
            totalEnemyUnits += 1


run_game( 
    maps.get("LightshadeAIE"),                 #mapa en el que se juega
    [Bot(Race.Terran, dummyBot()),                    #raza de nuestro bot
     Computer(Race.Random, Difficulty.VeryHard)],       #raza del enemigo y dificultad
     realtime=False                                #velocidad juego
)