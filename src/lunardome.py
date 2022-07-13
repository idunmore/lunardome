# Lunar Dome - Recreation of a text based game I originally wrote in Atari
#              Basic on the Atari 800 in 1979.
#
# Copyright (C) 2022, Ian Michael Dunmore
#
# MIT License: https://github.com/idunmore/lunardome/blob/main/LICENSE

from enum import Enum
import random
import sys

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
        self.year = 0
        self.__difficulty = DIFFICULTY_MULTIPLIER[difficulty]
        self.credits = int(5000 - 500 * (self.__difficulty -1))    
        self.colonists = 100
        self.__soup = 2000
        self.__oxygen = 3000
        self.__integrity = 100  
        self.soup_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))
        self.oxygen_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))
        self.sculpture_cost = random.randrange(2, 3 + int(self.__difficulty))
        # Initialize these values as part of the class definition ...        
        self.soup_cost = 0
        self.oxygen_cost = 0        
        self.sculpture_value = 0
        # ... and update them at initialization, and then per turn:
        self.update_per_turn_variables()       

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
        if value > 0 and value <= 100:
            self.__integrity = value
        elif value > 100:
            self.__integrity = 100
        else:
            self.__integriy = 0
       
    @property
    def maintenance_cost(self):
        return int((MAX_INTEGRITY - self.integrity) * self.difficulty) * 2

    @property
    def is_medium_or_lower_difficulty(self) -> bool:        
        return self.difficulty < (
            DIFFICULTY_MULTIPLIER[int(len(DIFFICULTY_MULTIPLIER)/2)])

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
        print(f"There are {self.colonists:,d} colonists living in the dome, "
            f"in year {self.year:,d}")      
        print(f"Available credits: {self.credits:,d}.")
        print(f"Dome integrity is at {self.integrity:d}%; "
            f"annual maintenance cost is {self.maintenance_cost:n} credits.")            
        print(f"Soup stocks stand at {self.soup:,d} units.")        
        print(f"Each colonist requires {self.soup_required_per_colonist:n} "
            f"units of Soup per year, at {self.soup_cost:n} credits per unit.")
        if self.is_medium_or_lower_difficulty:
            soup_lasts = int((self.soup
                / (self.colonists * self.soup_required_per_colonist)))
            print(f"Current Soup stocks will last {soup_lasts:n} years at "
                "present population.")
            soup_total_cost = (self.soup_cost
                * self.soup_required_per_colonist * self.colonists)         
            print("A one year supply of Soup for all colonists costs "
                f"{soup_total_cost:,d} credits.")            
        print(f"Oxygen tanks currently hold {self.oxygen:,d} units of Oxygen.")
        print(f"Each colonist requires {self.oxygen_required_per_colonist:n} "
            f"units of Oxygen per year, at {self.oxygen_cost:n} "
            "credits per unit.")
        if self.is_medium_or_lower_difficulty:
            oxygen_lasts = int((self.oxygen
                / (self.oxygen_required_per_colonist * self.colonists)))
            print(f"Current Oxygen stores will last {oxygen_lasts:n} years "
                "at present population.")
            oxygen_total_cost = (self.oxygen_cost
                * self.oxygen_required_per_colonist * self.colonists)
            print("A one year supply of Oxygen for all colonists costs "
                f"{oxygen_total_cost:,d} credits.")        
        print(f"Lunar Scuplutures cost {self.sculpture_cost:n} units of Oxygen "
            f"to make. They sell for {self.sculpture_value:n} credits.")

    def update_per_turn_variables(self):
        # Soup, Oxygen, Sculpture prices vary every turn.        
        self.soup_cost = random.randrange(3, 5 + int(self.__difficulty))
        self.oxygen_cost = random.randrange(3, 5 + int(self.__difficulty))       
        self.sculpture_value = (
            self.oxygen_cost * self.sculpture_cost + random.randrange(-2, 5))
        # Integrity and population change every turn AFTER the first year;
        # integrity reduces by percentage of colonists and colony grows.
        if self.year != 0:
            self.integrity -= int(self.colonists / 10)
            self.colonists += random.randrange(0, 2 + int(self.__difficulty))
            self.soup -= self.colonists * self.soup_required_per_colonist
            self.oxygen -= self.colonists * self.oxygen_required_per_colonist
        self.year += 1

    def perform_maintenance(self):
        if self.integrity == 100:
            print("No dome maintenance required this year.")
        elif self.credits >= self.maintenance_cost:
            self.credits -= self.maintenance_cost
            self.integrity = 100
            print(f"Dome repaired for {self.maintenance_cost:,d} credits.")
        else:
            print("Insufficient credits to repair dome.")    

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

    # Main game loop:
    while dome.is_viable:
        dome.display_state()
        print("")
        do_event(events, dome)
        
        buy_commodity(Commodity.OXYGEN, dome)
        buy_commodity(Commodity.SOUP, dome)
        make_scupltures(dome)    
        dome.perform_maintenance()
        dome.update_per_turn_variables()

    #for n in events:
    #    n.apply_event(dome_state)


    random.seed(1)

#    for n in range(0, 10):
#       print(random.randrange(1, 10))

    return

def buy_commodity(commodity: Commodity, dome_state: DomeState):

    match commodity:
        case Commodity.OXYGEN:
            can_afford = int(dome_state.credits/dome_state.oxygen_cost)
            commodity_name = "Oxygen"
            cost_per_unit = dome_state.oxygen_cost              
        case Commodity.SOUP:
            can_afford = int(dome_state.credits/dome_state.soup_cost)
            commodity_name = "Soup"
            cost_per_unit = dome_state.soup_cost              
        case Commodity.INTEGRITY:
            sys.exit("Cannot buy Integrity; Error in main gaim loop Logic.") 
    
    prompt = f"How many units of {commodity_name} do you want to buy"
    units = get_amount(prompt, can_afford)
    
    # Apply results of Purchase
    print(f"You bought {units:n} units of {commodity_name} for a total of "
        f"{units * cost_per_unit:n} credits.")

    # Update dome's commodity value
    if commodity == Commodity.OXYGEN:
        dome_state.oxygen += units
    else:
        dome_state.soup += units

    # Update credits
    dome_state.credits -= units * cost_per_unit
    print(f"You have {dome_state.credits:n} credits remaining.")

def make_scupltures(dome_state:DomeState):
    prompt = "How many Lunar Sculptures do you want to make and sell"
    can_afford = int(dome_state.oxygen / dome_state.sculpture_cost)
    sculptures = get_amount(prompt, can_afford)
    sculpture_profit = int(dome_state.sculpture_value * sculptures)
    sculpture_oxygen_usage = sculptures * dome_state.sculpture_cost
    print(f"You made {sculpture_profit:,d} credits selling Lunar Sculptures, "
        f"consuming {sculpture_oxygen_usage} units of Oxygen.")
    
    # Update oxygen used and credits earned
    dome_state.oxygen -= sculpture_oxygen_usage  
    dome_state.credits +=  sculpture_profit

def do_event(events, dome_state):
    # Events occur one turn in 10
    if random.randrange(0, 100) % 10 == 0:
        # Pick a random event and apply it ..
        events[random.randrange(0, len(events) - 1)].apply_event(dome_state)
        print("")


def get_amount(prompt, maximum) -> int:
    while True:
        print(f"{prompt}? [0-{maximum:,d}]? ", end="")
        entry = input()
        if entry.isnumeric():
            units = int(entry)
            if units >= 0 and units <= maximum:
                break
        print(f"You must enter a whole number between 0 and {maximum:,d}.")

    return units



def show_instructions():
    pass

# Run!
if __name__ == '__main__':
    lunardome() 