import mesa
from my_project.random_walk import RandomWalker
from enum import Enum

class PoliticalParty(Enum):
    BLUE = 1
    GRAY = 2
    RED = 3

class PoliticalAgent(mesa.Agent):
    """
    Base for any Agent with political party

    Attributes:
        Political Party Inclination:
            Democrat (Blue) : from 0 - 127
            None (Gray)     : 128
            Republican (Red): from 129 - 256
    """

    def __init__(self, unique_id, pos, model, political_party_inclination):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.pos = pos

        self.political_party_inclination = political_party_inclination
        self.political_party = self.get_party()

    def get_party(self):
        if self.political_party_inclination < 128:
            return PoliticalParty.BLUE
        elif self.political_party_inclination > 128:
            return PoliticalParty.RED
        else:
            return PoliticalParty.GRAY

    def update_party(self):
        self.political_party = self.get_party()

    def set_party(self, party):
        self.political_party = party

class Person(PoliticalAgent):
    """
    A person walks around, reproduces ? and dies.

    The init is the same as the RandomWalker.
    """

    def __init__(self, unique_id, pos, model, political_party_inclination, age=20, max_age=80, influence=1, is_influencer=False):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        """
        super().__init__(unique_id, pos, model, political_party_inclination)
        self.pos = pos

        self.age = age
        self.max_age = max_age
        self.influence = influence
        self.is_influencer = is_influencer

    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

    def step(self):
        """
        A model step. Move, then share & consume and reproduce.
        """
        # Increase age
        self.age += 1

        # Move
        self.random_move()

        # Consumes & shares
        neighbors = self.get_people()
        people = [obj for obj in neighbors if isinstance(obj, (Person, Influencer))]
        
        for person in people:
            # Share to people? or is redundant?
            self.share_ideas(person)
            # self.consumes_ideas(person)
        
        self.update_party()

        if(self.model.is_mortal):
            # Reproduce
            if self.age > 18 and self.random.random() < self.model.person_reproduce:
                self.reproduce()

            # Death
            if self.age > self.max_age:
                self.die()

    def reproduce(self):
        # Create a new person:
        offspring = Person(
            self.model.next_id(), self.pos, self.model, self.political_party_inclination, 0, self.max_age
        )
        self.model.grid.place_agent(offspring, self.pos)
        self.model.schedule.add(offspring)

    def die(self):
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)
            
    def get_people(self):
        people = []
        neighborhood = self.model.grid.get_neighborhood(self.pos,True, self.influence)

        # Equivalent to:
        for cell in neighborhood:
            contents = self.model.grid.get_cell_list_contents(cell)
            for person in contents:
                people.append(person)
        # people = [person for cell in neighborhood for person in self.model.grid.get_cell_list_contents(cell)]

        return people
    
    # age determines how influenced is by others
        # young age < 18 -> very influenced
        # old   age > 50 -> low influenced
    def consumes_ideas(self, agent):
        #print("before political inclination=",self.political_party_inclination)
        political_difference = agent.political_party_inclination - self.political_party_inclination
        #print("political difference=",political_difference)
        political_influence = political_difference * self.model.proximity_influence
        if agent.is_influencer:
            political_influence *= 1 + self.model.influencer_influence
        if self.age < 18 or self.age > 50:
            political_influence *= 1.25 if self.age < 18 else .75

        self.political_party_inclination += round(political_influence)
        self.political_party_inclination = clamp(self.political_party_inclination,0,256)
        #print("post political inclination=",self.political_party_inclination)

    def share_ideas(self, agent):
        if(self.model.influencer_changes and isinstance(agent,Influencer)):
            agent.consumes_ideas(self)

# remove influencer class and use only person with flag?
class Influencer(Person):
    """
    This person will have a greater impact in media
    """
    def __init__(self, unique_id, pos, model, political_party_inclination, age=20, max_age=80, influence=2, followers=100):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, pos, model, political_party_inclination, age, max_age, influence, True)
        self.followers = followers

    def reproduce(self):
        # Create a new person:
        offspring = Influencer(
            self.model.next_id(), self.pos, self.model, self.political_party_inclination, 0, self.max_age
        )
        self.model.grid.place_agent(offspring, self.pos)
        self.model.schedule.add(offspring)

class Territory(PoliticalAgent):
    """
        In setup a number of territories (countries) will form.

        The territories will change color depending on 
        the average political party of the citizens
    """
    def __init__(self, unique_id, pos, model, territory_id=None, is_capital=False, capital=None,political_party_inclination=128):
        """
        Creates a new patch of grass
        """
        
        super().__init__(unique_id, pos, model, political_party_inclination)

        self.territory_id = territory_id
        self.is_capital = is_capital
        if(is_capital):
            self.territory = []
        else:
            self.capital = capital

    def step(self):
        # if(self.is_capital):
            # print("capital ",self.territory_id," Territory = ", self.territory)
        self.update_party()

    def set_territory_id(self, territory_id):
        self.territory_id = territory_id

    def add_territory(self, patch):
        self.territory.append(patch)

    def get_territory(self):
        return self.territory
    
    def get_patch(self, pos):
        contents = self.model.grid.get_cell_list_contents(pos)

        for agent in contents:
            if(isinstance(agent, Territory)):
                return agent
            
        return None
    
    def get_people(self, pos):
        people = []
        contents = self.model.grid.get_cell_list_contents(pos)

        for agent in contents:
            if(isinstance(agent, (Person, Influencer))):
                people.append(agent)
            
        return people
    
    def get_territory_patches(self):
        patches = []
        neighborhood = self.get_territory()

        for cell in neighborhood:
            patch = self.get_patch(cell)
            if(patch is not None):
                patches.append(patch)

        return patches
    
    def get_territory_people(self):
        population = []
        neighborhood = self.get_territory()

        for cell in neighborhood:
            people = self.get_people(cell)
            population += people

        return population
    
    def count_party(self):
        # in order [BLUE, GRAY, RED] or [democrat, none, republican]
        population_party = {PoliticalParty.BLUE:0,PoliticalParty.GRAY:0,PoliticalParty.RED:0}

        population = self.get_territory_people()

        for person in population:
            population_party[person.political_party] += 1

        # print("capital ",self.territory_id," population party = ", population_party)
        
        return population_party
    
    def get_territory_party(self):
        territory_count_party = self.count_party()
        party = max(territory_count_party,key=lambda k: territory_count_party[k])

        return party
    
    def update_party(self):
        if(self.is_capital):
            self.political_party = self.get_territory_party()
            # print("capital ",self.territory_id," party = ", self.political_party)
        else:
            self.political_party = self.get_patch(self.capital).political_party

def clamp(value, smallest, largest):
    return max(smallest, min(value, largest))