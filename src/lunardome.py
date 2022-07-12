# Lunar Dome - Recreation of a text based game I originally wrote in Atari
#              Basic on the Atari 800 in 1979.
#
# Copyright (C) 2022, Ian Michael Dunmore
#
# MIT License: https://github.com/idunmore/lunardome/blob/main/LICENSE

from enum import Enum
import random

# Constants
MAX_INTEGRITY = 100

DIFFICULTY_MULTIPLIER = [1, 1.25, 1.5, 1.75, 2.00]

class EventType(Enum): 
    BOON = 0
    CALAMITY = 1

class Commodity(Enum):
    OXYGEN = 0
    SOUP = 1
    INTEGRITY = 2

class DomeState():
    def __init__(self, difficulty):
        self.year = 1
        self.__difficulty = DIFFICULTY_MULTIPLIER[difficulty]
        self.credits = int(5000 - 500 * (self.__difficulty -1))    
        self.colonists = 100
        self.__soup = 2000
        self.__oxygen = 3000
        self.__integrity = 100  
        # Initialize these values as part of the class definition ...
        self.soup_required_per_colonist = 0
        self.oxygen_required_per_colonist = 0
        self.soup_cost = 0
        self.oxygen_cost = 0        
        self.sculpture_value = 0
        self.sculpture_cost = 0
        # ... and update them at initialization, and then per turn:
        self.update_costs_and_requirements()       

    @property
    def difficulty(self):
        return self.__difficulty

    @property
    def soup(self):
        return self.__soup
    
    @soup.setter
    def soup(self, value):
        self.__soup = value if value > 0 else 0

    @property
    def oxygen(self):
        return self.__oxygen
    
    @soup.setter
    def oxygen(self, value):
        self.__oxygen = value if value > 0 else 0
        
    @property
    def integrity(self):
        return self.__integrity

    @integrity.setter
    def integrity(self, value):
        self.__integrity = value if value > 0 else 0

    @property
    def maintenance_cost(self):
        return int((MAX_INTEGRITY - self.integrity) * self.difficulty) * 2

    @property
    def is_medium_or_lower_difficulty(self) -> bool:        
        return self.difficulty < (
            DIFFICULTY_MULTIPLIER[int(len(DIFFICULTY_MULTIPLIER)/2)+1])
    @property
    def is_viable(self) -> bool:
        # If any commodity is exhausted, or insufficient for the current year,
        # then the Dome is not longer viable.

        # Enough Oxygen?
        if (self.oxygen_required_per_colonist * self.colonists >= self.__oxygen 
            or self.__oxygen <= 0):
            return False
        
        # Enough Soup?
        if (self.soup_required_per_colonist * self.colonists >= self.__soup
            or self.__soup <= 0):
            return False
        
        # Dome has some Integrity left?
        if self.integrity <= 0: return False
        
        # All conditions above must be met, for Dome to be Viable.
        return True

    def display_state(self):       
        print("There are {colonists:,d} colonists living in the dome, "
            "in year {year:d}."
            .format(colonists = self.colonists, year = self.year))
        print("Available credits: {credits:,d}.".format(credits = self.credits))
        print("Dome integrity is at {integrity:d}%; "
            "annual maintenance cost is {maintenance:n} credits."
            .format(integrity = self.integrity, maintenance = 
                self.maintenance_cost))
        print("Soup stocks stand at {soup:,d} units.".format(soup = self.soup))
        print("Each colonist requires {req:n} units of Soup per year."        
            .format(req = self.soup_required_per_colonist))
        print("Soup costs {cost:n} credits per unit."
            .format(cost = self.soup_cost))
        if self.is_medium_or_lower_difficulty:            
            print("A one year supply of Soup for all colonists costs "
                "{cost:,d} credits."
                .format(cost = 
                    self.soup_cost * self.soup_required_per_colonist
                    * self.colonists))
        print("Oxygen tanks currently hold {oxygen:,d} units of Oxygen."
            .format(oxygen = self.oxygen))
        print("Each colonist requires {req:n} units of Oxygen per year."
            .format(req = self.oxygen_required_per_colonist))
        print("Oxygen costs {cost:n} credits per unit."
            .format(cost = self.oxygen_cost))
        if self.is_medium_or_lower_difficulty:
            print("A one year supply of Oxygen for all colonists costs "
                "{cost:,d} credits."
                .format(cost = 
                    self.oxygen_cost * self.oxygen_required_per_colonist
                    * self.colonists))        
        print("Lunar Scuplutures currently cost {cost:n} units of Oxygen to "
            "make. They sell for {value:n} credits."
            .format(cost = self.sculpture_cost, value = self.sculpture_value,))

    def update_costs_and_requirements(self):
        self.soup_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))
        self.oxygen_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))
        self.soup_cost = random.randrange(3, 5 + int(self.__difficulty))
        self.oxygen_cost = random.randrange(3, 5 + int(self.__difficulty))
        self.sculpture_cost = random.randrange(2, 3 + int(self.__difficulty))
        self.sculpture_value = (
            self.oxygen_cost * self.sculpture_cost + random.randrange(-2, 5))
        if self.year != 1: self.integrity -= random.randrange(2, 5)       

class Event():
    def __init__(self, event_type, commodity, minimum, maximum, message):
        self.event_type = event_type
        self.commodity = commodity
        self.minimum = minimum
        self.maximum = maximum
        self.message = message
        self.amount = 0
        
    def apply_event(self, dome_state):
        # Amount is a random value, in a specified range.  For "calamaties",
        # this is then adjusted by a difficulty modifier.  Sign is set depending
        # on whether it is a Calamity (-) or a Boon (+).
        value = random.randrange(self.minimum, self.maximum)
        if self.event_type == EventType.BOON:
            self.amount = value
        else:
            self.amount = -abs(value * dome_state.difficulty)        

        # Adjust the appropriate Dome State commodity; since we're using
        # signed amounts we can simply ADD the value.
        match self.commodity:
            case Commodity.OXYGEN:
                dome_state.oxygen += self.amount                
            case Commodity.SOUP:
                dome_state.soup += self.amount                
            case Commodity.INTEGRITY:
                dome_state.integrity += self.amount                

        self.__display()

    def __display(self):
        print(self.message.format(units=abs(self.amount)))


# Calamities and Boons

class SoupDragon(Event):
    def __init__(self):        
        super().__init__(EventType.CALAMITY, Commodity.SOUP, 20, 100,            
            "The Soup Dragon visits; it slurps {units:n} units of Soup!")

class MeteorStrike(Event):
    def __init__(self):
        super().__init__(EventType.CALAMITY, Commodity.INTEGRITY, 10, 45,
            "A Meteor strikes the dome; Dome Integrity reduced by {units:n}!")

class MoonQuake(Event):
    def __init__(self):
        super().__init__(EventType.CALAMITY, Commodity.OXYGEN, 20, 100,
            "A Moon Quake damages Oxygen storage; you lose {units:n} units!")
        
class IronChicken(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.OXYGEN, 20, 100,
            "The Iron Chicken visits; it deposits {units:n} units of Oxygen!")

class SoupGeyser(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.SOUP, 20, 100,
            "A Soup Geyser erupts; you harvest {units:n} units of Soup!")

class Astronaut(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.INTEGRITY, 10, 50,
            "An Astronaut arrives; they restore Dome Intregity by {units:n}!")

# Main Game Loop
def lunardome():

    events = [
        SoupDragon(), MeteorStrike(), MoonQuake(), IronChicken(), SoupGeyser(),
        Astronaut()
    ]
    
    dome = DomeState(0)
    dome.display_state()

    #for n in events:
    #    n.apply_event(dome_state)


    random.seed(1)

#    for n in range(0, 10):
#       print(random.randrange(1, 10))

    return

def show_instructions():
    pass

# Run!
if __name__ == '__main__':
    lunardome() 