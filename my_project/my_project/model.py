"""
Political Evolution Model
================================
TODO INFO
"""

import mesa

from my_project.scheduler import RandomActivationByTypeFiltered, BaseActivationByTypeFiltered
from my_project.agents import Person, Influencer, Territory, PoliticalParty
import random

class Simulation(mesa.Model):
    """
    Political Evolution Model
    """

    # width = 20
    # height = 20

    # initial_person = 100
    # initial_influencer = 50
    # initial_political = 128

    # person_reproduce = 0.04
    # influencer_reproduce = 0.07

    # number_territory = 4

    # max_age = 80
    # proximity_influence = 0.3
    # influencer_influence = 0.3

    # enable_influencer = False
    # enable_territory = False

    verbose = False  # Print-monitoring

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        width=20,
        height=20,
        initial_person=100,
        initial_influencer=50,
        initial_percentage=0,
        person_reproduce=0.04,
        influencer_reproduce=0.05,
        number_territory=4,
        is_mortal=True,
        max_age=80,
        proximity_influence=0.3,
        influencer_influence=0.3,
        influencer_changes=True,
        enable_influencer=False,
        enable_territory=False,
        is_hex=False
    ):
        # TODO update Args
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_person
            initial_influencer
            initial_political
            person_reproduce
            influencer_reproduce
            enable_influencer
            enable_territory

            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        """
        super().__init__()
        # Set parameters
        self.is_hex = is_hex
        self.width = width
        self.height = height
        self.initial_person=initial_person
        self.initial_influencer=initial_influencer
        self.initial_percentage=initial_percentage
        self.person_reproduce=person_reproduce
        self.influencer_reproduce=influencer_reproduce
        self.number_territory=number_territory
        self.proximity_influence=proximity_influence
        self.is_mortal=is_mortal
        self.max_age=max_age
        self.influencer_influence=influencer_influence
        self.influencer_changes=influencer_changes
        self.enable_influencer=enable_influencer
        self.enable_territory=enable_territory

        self.schedule = RandomActivationByTypeFiltered(self)
        self.schedule_patch = BaseActivationByTypeFiltered(self)
        if(is_hex):
            self.grid = mesa.space.HexGrid(self.width, self.height, torus=True)
        else:
            self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)

        
        self.datacollector = mesa.DataCollector(
            {
                "Person": lambda m: m.schedule.get_type_count(Person),
                "Influencer": lambda m: m.schedule.get_type_count(Influencer),
                "Republican": lambda m: m.schedule.get_type_count(
                    Person, lambda x: x.political_party == PoliticalParty.RED) +
                    m.schedule.get_type_count(
                    Influencer, lambda x: x.political_party == PoliticalParty.RED),
                "Democrat": lambda m: m.schedule.get_type_count(
                    Person, lambda x: x.political_party == PoliticalParty.BLUE) +
                    m.schedule.get_type_count(
                    Influencer, lambda x: x.political_party == PoliticalParty.BLUE),
                "None": lambda m: m.schedule.get_type_count(
                    Person, lambda x: x.political_party == PoliticalParty.GRAY) +
                    m.schedule.get_type_count(
                    Influencer, lambda x: x.political_party == PoliticalParty.GRAY),
                "Republican Spaces": lambda m: m.schedule_patch.get_type_count(
                    Territory, lambda x: x.political_party == PoliticalParty.RED),
                "Democrat Spaces": lambda m: m.schedule_patch.get_type_count(
                    Territory, lambda x: x.political_party == PoliticalParty.BLUE),
            }
        )

        # Create territory patches
        if self.enable_territory:
            self.setup_territories()

        # Create person:
        for i in range(self.initial_person):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            political = 256 if i < self.initial_person * self.initial_percentage else 0
            age = self.random.randrange(self.max_age)
            person = Person(self.next_id(), (x, y), self, political, age, self.max_age)
            self.grid.place_agent(person, (x, y))
            self.schedule.add(person)

        # Create influencer
        if self.enable_influencer:
            for i in range(self.initial_influencer):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                political = 256 if i < self.initial_influencer * self.initial_percentage else 0
                age = self.random.randrange(self.max_age)
                followers = self.random.randrange(1000)
                influencer = Influencer(self.next_id(), (x, y), self, political, age, self.max_age, self.influencer_influence, followers)
                self.grid.place_agent(influencer, (x, y))
                self.schedule.add(influencer)

        self.running = True
        self.datacollector.collect(self)

    def setup_territories(self):
        # Random create capitals for each
        capitals = list(zip(
                random.sample(range(self.width), self.number_territory),
                random.sample(range(self.height), self.number_territory),
                range(self.number_territory)
            ))
        print("capitals=",capitals)
        
        # Creating capitals of the Territory
        capitals_agents = []
        for x, y, territory_id in capitals:
            patch = Territory(self.next_id(), (x, y), self, territory_id, is_capital=True)
            self.grid.place_agent(patch, (x, y))
            self.schedule_patch.add(patch)
            capitals_agents.append(patch)
        
        # Expanding capitals by neighborhoods
        radius = 1
        while len(self.grid.empties) != 0:
            for x, y, territory_id in capitals:
                if(self.is_hex):
                    neighborhood = self.grid.get_neighborhood((x, y),False, radius)
                else:
                    neighborhood = self.grid.get_neighborhood((x, y), True, False, radius)
                print("\tterritory_id=",territory_id," neighborhood=",len(neighborhood))
                for neighbor in neighborhood:
                    if self.grid.empties == 0:
                        break
                    if self.grid.is_cell_empty(neighbor):
                        print("\t\tneigbor is empty=",neighbor)
                        patch = Territory(self.next_id(), neighbor, self, territory_id, capital=(x,y))
                        self.grid.place_agent(patch, neighbor)
                        self.schedule_patch.add(patch)
                        capitals_agents[territory_id].add_territory(neighbor)
                    
            print("radius=",radius,' empties=',len(self.grid.empties))
            radius += 1

    def step(self):
        self.schedule.step()
        self.schedule_patch.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_type_count(Person),
                    self.schedule.get_type_count(Influencer),
                    self.schedule.get_type_count(
                    Person, lambda x: x.political_party == PoliticalParty.RED),
                    self.schedule.get_type_count(
                    Person, lambda x: x.political_party == PoliticalParty.BLUE),
                    self.schedule_patch.get_type_count(
                    Territory, lambda x: x.political_party == PoliticalParty.RED),
                    self.schedule_patch.get_type_count(
                    Territory, lambda x: x.political_party == PoliticalParty.BLUE),
                ]
            )

    def run_model(self, step_count=200):

        if self.verbose:
            print(
                "Initial number Republican: ", 
                self.schedule.get_type_count(Person, lambda x: x.political_party == PoliticalParty.RED)
            )
            print(
                "Initial number Democrat: ", 
                self.schedule.get_type_count(Person, lambda x: x.political_party == PoliticalParty.BLUE)
            )
            print(
                "Initial number Republican Territory: ",
                self.schedule_patch.get_type_count(Territory, lambda x: x.political_party == PoliticalParty.RED),
            )
            print(
                "Initial number Democrat Territory: ",
                self.schedule_patch.get_type_count(Territory, lambda x: x.political_party == PoliticalParty.BLUE),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Final number Republican: ", 
                self.schedule.get_type_count(Person, lambda x: x.political_party == PoliticalParty.RED)
            )
            print(
                "Final number Democrat: ", 
                self.schedule.get_type_count(Person, lambda x: x.political_party == PoliticalParty.BLUE)
            )
            print(
                "Final number Republican Territory: ",
                self.schedule_patch.get_type_count(Territory, lambda x: x.political_party == PoliticalParty.RED),
            )
            print(
                "Final number Democrat Territory: ",
                self.schedule_patch.get_type_count(Territory, lambda x: x.political_party == PoliticalParty.BLUE),
            )
