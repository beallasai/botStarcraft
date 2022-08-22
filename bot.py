import sc2
from sc2.bot_ai import BotAI  
from sc2.data import Difficulty, Race 
from sc2.main import run_game  
from sc2.player import Bot, Computer  
from sc2 import maps  
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit

class SCBot(BotAI):


    async def on_step(self, iteration: int):
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},", \
            f"minerals: {self.minerals}, gas: {self.vespene}, atacantes: {self.units(UnitTypeId.REAPER).amount},", \
            f"commandCenter:{self.structures(UnitTypeId.COMMANDCENTER).amount}, supply: {self.supply_used}/{self.supply_cap}")
        

        await self.distribute_workers()


        #2 centros de mando
        command_center = self.townhalls.random

        # if 1 <= self.townhalls.amount < 2 and self.already_pending(UnitTypeId.COMMANDCENTER) == 0 and self.can_afford(UnitTypeId.COMMANDCENTER):
        #     location: Point2 = await self.get_next_expansion()
        #     if location:
        #         worker: Unit = self.select_build_worker(location)
        #         if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
        #             worker.build(UnitTypeId.COMMANDCENTER, location)

        #creamos obreros
        if self.can_afford(UnitTypeId.SCV) and command_center.is_idle:
            if self.supply_workers + self.already_pending(UnitTypeId.SCV) < 20 * self.structures(UnitTypeId.COMMANDCENTER).amount:
                command_center.train(UnitTypeId.SCV)  
        
        
        # if command_center.is_idle and self.can_afford(UnitTypeId.SCV) and self.workers.amount < 25:     
        #     command_center.train(UnitTypeId.SCV)         

        #depositos de suministros 
        elif self.supply_left < 3:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 2:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=command_center.position.towards(self.game_info.map_center, 8))

        # elif self.structures(UnitTypeId.SUPPLYDEPOT).amount < 5:
        #     if self.can_afford(UnitTypeId.SUPPLYDEPOT) and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
        #         await self.build(UnitTypeId.SUPPLYDEPOT, near=command_center)

        #refinerias
        elif self.structures(UnitTypeId.REFINERY).amount < 2:
            for command_center in self.structures(UnitTypeId.COMMANDCENTER):
                gases = self.vespene_geyser.closer_than(20, command_center)
                for gas in gases:
                    if self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.REFINERY):
                        await self.build(UnitTypeId.REFINERY, gas)

        #barracones
        if self.structures(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.BARRACKS) and self.structures(UnitTypeId.BARRACKS).amount < 3 and not self.already_pending(UnitTypeId.BARRACKS):
                await self.build(UnitTypeId.BARRACKS, near=command_center.position.towards(self.game_info.map_center, 8))

        # elif self.structures(UnitTypeId.BARRACKS).amount < 3:
        #     if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
        #         await self.build(UnitTypeId.BARRACKS, near=command_center)

            
            
        #     #fabricas
        #     position: Point2 = command_center.position.towards_with_random_angle(self.game_info.map_center, 16)
        #     if self.structures(UnitTypeId.BARRACKS).ready:
        #         if self.structures(UnitTypeId.FACTORY).amount < 3 and not self.already_pending(UnitTypeId.FACTORY) and self.can_afford(UnitTypeId.FACTORY):
        #             await self.build(UnitTypeId.FACTORY, near=position)

        #         if self.structures(UnitTypeId.FACTORY).ready:
        #             await self.build(UnitTypeId.FACTORYTECHLAB, near=position)


        # for factory in self.structures(UnitTypeId.FACTORYTECHLAB).ready.idle:
        #     if self.can_afford(UnitTypeId.CYCLONE):
        #         factory.train(UnitTypeId.CYCLONE)


        #creamos marines
        if self.units(UnitTypeId.MARINE).amount < 15 :
            for barrack in self.structures(UnitTypeId.BARRACKS).ready.idle:
                if self.can_afford(UnitTypeId.REAPER) and not self.already_pending(UnitTypeId.REAPER):
                    barrack.train(UnitTypeId.REAPER)



        # si no tenemos centro de mando y podemos hacerlo, se hace
        # else:                                              
        #     if self.can_afford(UnitTypeId.COMMANDCENTER):
        #         await self.expand_now()




run_game( 
    maps.get("2000AtmospheresAIE"),                 #mapa en el que se juega
    [Bot(Race.Terran, SCBot()),                    #raza de nuestro bot
     Computer(Race.Random, Difficulty.Hard)],       #raza del enemigo y dificultad
     realtime=False                                #velocidad juego
)