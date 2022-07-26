from sc2.bot_ai import BotAI  
from sc2.data import Difficulty, Race 
from sc2.main import run_game  
from sc2.player import Bot, Computer  
from sc2 import maps  
from sc2.ids.unit_typeid import UnitTypeId

class dummyBot(BotAI):

    async def on_step(self,iteration):
        await self.distribute_workers()             #distribución de obreros para recolectar

        command_center = self.townhalls.random      #entre los centros de mando que tengamos

        if command_center.is_idle and self.can_afford(UnitTypeId.SCV):      #se crean obreros siempre que se pueda
            command_center.train(UnitTypeId.SCV)

        #mandar a un scout al empezar
        if iteration==0:
            scout = self.workers[0]
            scout.attack(self.enemy_start_locations[0])


run_game( 
    maps.get("LightshadeAIE"),                 #mapa en el que se juega
    [Bot(Race.Terran, dummyBot()),                    #raza de nuestro bot
     Computer(Race.Random, Difficulty.Hard)],       #raza del enemigo y dificultad
     realtime=False                                #velocidad juego
)