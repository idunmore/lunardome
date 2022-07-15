# Lunar Dome - Recreation of a text based game I wrote in Atari Basic on the 
#              Atari 800, inspired by Tim Hartnell's "Dome Dweller" from
#              "The Book of Listings" and "Games for Your Atari".
#
# Copyright (C) 2022, Ian Michael Dunmore
#
# MIT License: https://github.com/idunmore/lunardome/blob/main/LICENSE

from enum import Enum
import random
import sys
import os
from sty import fg, ef

# Constants
MAX_INTEGRITY = 100

# Multiplier for each difficulty "level"; higher numbers = harder.
DIFFICULTY_MULTIPLIER = [1, 1.25, 1.5, 1.75, 2.00]

# Text color/effect aliases (from "sty" module values).  C_ prefix = "Color".
# Abbreviations are used to reduce line-length in text output functions.  
C_SOUP = fg.yellow      # Soup
C_EMPH = fg.white       # Emphasis
C_OXY = fg.li_blue      # Oxygen
C_SCULPT = fg.magenta   # Lunar Scupltures
C_INTEG = fg.cyan       # Dome Integrity
C_GOOD = fg.green       # Good/Boon
C_BAD = fg.red          # Bad/Calamity/Warning
C_EASY = fg.green       # Easy
C_HARD = fg.red         # Hard
C_OFF = fg.rs + ef.rs   # Default State Color (Color "OFF", Effects "OFF")

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
        self.end_turn()       

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
    
    @oxygen.setter
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
            self.__integrity = 0
       
    @property
    def maintenance_cost(self):
        return int((MAX_INTEGRITY - self.integrity) * self.difficulty) * 2

    @property
    def is_medium_or_lower_difficulty(self) -> bool:        
        return self.difficulty < (
            DIFFICULTY_MULTIPLIER[int(len(DIFFICULTY_MULTIPLIER)/2)])

    @property
    def is_viable(self) -> bool:
        # If any commodity is exhausted, the dome is no longer viable.
        if self.oxygen <= 0 or self.soup <= 0 or self.integrity <= 0:
             return False     
        else:
            return True

    def display(self):
        clear_screen()
        print(f"There are {ef.bold}{self.colonists:,d}{fg.rs}{ef.rs} colonists "
            f"living in the dome, in year {fg.green}{self.year:,d}{fg.rs}.")      
        print(f"Available credits: {fg.green}{self.credits:,d}{fg.rs}.")
        print(f"Dome integrity is at {self.integrity:d}%; annual maintenance "
            f"cost is {fg.green}{self.maintenance_cost:n}{fg.rs} credits.")            
        print(f"Soup stocks stand at {self.soup:,d} units.")        
        print(f"Each colonist requires {self.soup_required_per_colonist:n} "
            f"units of Soup per year, at {self.soup_cost:n} credits per unit.")
        if self.is_medium_or_lower_difficulty:
            soup_lasts = int((self.soup
                / (self.colonists * self.soup_required_per_colonist))) 
            print(f"Current Soup stocks will last about {soup_lasts:n} years "
                "at present population.")
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
            print(f"Current Oxygen stores will last about {oxygen_lasts:n} "
                "years at present population.")
            oxygen_total_cost = (self.oxygen_cost
                * self.oxygen_required_per_colonist * self.colonists)
            print("A one year supply of Oxygen for all colonists costs "
                f"{oxygen_total_cost:,d} credits.")                  
        print(f"Lunar Scuplutures cost {self.sculpture_cost:n} units of Oxygen "
            f"to make. They sell for {self.sculpture_value:n} credits.")
        print("")

    def end_turn(self):
        # Soup, Oxygen, Sculpture prices vary every turn.        
        self.soup_cost = random.randrange(3, 5 + int(self.__difficulty))
        self.oxygen_cost = random.randrange(3, 5 + int(self.__difficulty))       
        self.sculpture_value = (
            self.oxygen_cost * self.sculpture_cost + random.randrange(-2, 5))
        # Integrity and population change every turn AFTER the first year;
        # integrity reduces by percentage of colonists and colony grows.
        if self.year != 0:
            self.soup -= self.colonists * self.soup_required_per_colonist
            self.oxygen -= self.colonists * self.oxygen_required_per_colonist
            self.integrity -= int(self.colonists / 10)
            # Update colonists LAST, so as not to skew calcs for CURRENT year.
            # Colony increases by PERCENTAGE, to simulate accelerating growth.
            modifier = int(self.difficulty) * 10          
            increase_percent = 1 + random.randrange(1, modifier) / 100                 
            self.colonists = int(self.colonists * increase_percent)           
            
        self.year += 1

    def perform_maintenance(self):
        if self.integrity == 100:
            print(f"{fg.green}No dome maintenance required this year.{fg.rs}")
        elif self.credits >= self.maintenance_cost:
            print(f"Dome {fg.green}repaired{fg.rs} for "
                f"{fg.white}{self.maintenance_cost:,d}{fg.rs} credits; now at "
                f"{fg.green}100%{fg.li_cyan} Integrity{fg.rs}.")
            self.credits -= self.maintenance_cost
            self.integrity = 100
            
        else:
            print(f"{fg.red}Insufficient credits to repair dome.{fg.rs}")    

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
        # Display BOONs in Green, CALAMITIES in Red
        color = "green" if self.event_type == EventType.BOON else "red"
        print(fg(color) + self.message.format(units=abs(self.amount)) + fg.rs)       

# Calamities and Boons
class SoupDragon(Event):
    def __init__(self):        
        super().__init__(EventType.CALAMITY, Commodity.SOUP, 100, 300,            
            "The Soup Dragon visits; it slurps {units:n} units of Soup!")

class MeteorStrike(Event):
    def __init__(self):
        super().__init__(EventType.CALAMITY, Commodity.INTEGRITY, 10, 45,
            "A Meteor strikes the dome; Dome Integrity reduced by {units:n}!")

class MoonQuake(Event):
    def __init__(self):
        super().__init__(EventType.CALAMITY, Commodity.OXYGEN, 100, 300,
            "A Moon Quake damages Oxygen storage; you lose {units:n} units!")
        
class IronChicken(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.OXYGEN, 100, 300,
            "The Iron Chicken visits; it deposits {units:n} units of Oxygen!")

class SoupGeyser(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.SOUP, 100, 300,
            "A Soup Geyser erupts; you harvest {units:n} units of Soup!")

class Astronaut(Event):
    def __init__(self):
        super().__init__(EventType.BOON, Commodity.INTEGRITY, 10, 45,
            "An Astronaut arrives; they restore Dome Integrity by {units:n}%!")

# Main Game Loop
def lunardome():

    events = [
        SoupDragon(), MeteorStrike(), MoonQuake(), IronChicken(), SoupGeyser(),
        Astronaut()
    ]
    
    show_instructions()

    # Get desired difficulty level, and setup Dome accordingly.
    difficulty = choose_difficulty()  
    dome = DomeState(difficulty)   

    # Main game loop:
    while dome.is_viable:
        dome.display()        
        random_event(events, dome)        
        buy_commodity(Commodity.OXYGEN, dome)
        buy_commodity(Commodity.SOUP, dome)
        make_scupltures(dome)    
        dome.perform_maintenance()        
        dome.end_turn()
        print("\nPress [Enter] for next turn.", end="")
        input()

    # Game Over ...
    print(f"Game Over in {dome.year:n} years!")

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
    
    prompt = f"How many units of {commodity_name} do you want to buy?"
    units = get_amount(prompt, 0, can_afford)
    
    # Apply results of Purchase
    print(f"You bought {units:n} units of {commodity_name} for a total of "
        f"{units * cost_per_unit:n} credits.")

    # Update purchased commodity value
    if commodity == Commodity.OXYGEN:
        dome_state.oxygen += units
    else:
        dome_state.soup += units

    # Update credits
    dome_state.credits -= units * cost_per_unit
    print(f"You have {dome_state.credits:n} credits remaining.")

def make_scupltures(dome_state:DomeState):
    prompt = "How many Lunar Sculptures do you want to make and sell?"
    can_afford = int(dome_state.oxygen / dome_state.sculpture_cost)
    sculptures = get_amount(prompt, 0, can_afford)
    sculpture_profit = dome_state.sculpture_value * sculptures
    sculpture_oxygen_usage = sculptures * dome_state.sculpture_cost
    print(f"You made {sculpture_profit:,d} credits selling Lunar Sculptures, "
        f"consuming {sculpture_oxygen_usage} units of Oxygen.")
    
    # Update oxygen used and credits earned    
    dome_state.oxygen -= sculpture_oxygen_usage     
    dome_state.credits +=  sculpture_profit

def random_event(events, dome_state):
    # Events occur one turn in 10
    if random.randrange(0, 100) % 10 == 0:
        # Pick a random event and apply it ..
        events[random.randrange(0, len(events) - 1)].apply_event(dome_state)
        print("")

def get_amount(prompt, minimum, maximum) -> int:
    while True:
        print(f"{prompt} [{minimum:,d} - {maximum:,d}]: ", end="")
        entry = input()
        if entry.isnumeric():
            units = int(entry)
            if units >= minimum and units <= maximum:
                break
        print(f"You must enter a whole number between {minimum:,d} and "
            f"{maximum:,d}.")

    return units

def clear_screen():
    _ = os.system("cls" if os.name=="nt" else "clear")

def show_title():
    pass

def choose_difficulty() -> int:    
    print(f"{C_EMPH}Lunar Dome - Choose Difficulty Level:{C_OFF}\n\n"
        f"{C_EMPH}Lunar Dome{C_OFF} offers {C_EMPH}five{C_OFF} levels of "
        f"progressive difficulty with {C_EASY}1{C_OFF} being the {C_EASY}"
        f"easiest{C_OFF}\nand {C_HARD}5{C_OFF} the {C_HARD}hardest{C_OFF}.\n\n"
        f"At higher difficulty levels, there is:\n\n"
        f" * More variation in the cost/value for {C_OXY}Oxygen{C_OFF}, "
        f"{C_SOUP}Soup{C_OFF} and {C_SCULPT}'Lunar Sculptures'{C_OFF}.\n"
        f" * A reduction in the number of starting {C_EMPH}Credits{C_OFF}.\n"
        f" * An increase in how fast the population of the colony grows.\n"
        f" * An increase in the negative impact of {C_BAD}Calamities{C_OFF} "
        f"vs. {C_GOOD}Boons{C_OFF}.\n"
        f" * Elimination of low-commodity warnings and estimates.\n"
    )

    prompt = (
        f"Enter Difficulty ({C_EASY}1=Easy{C_OFF}, {C_HARD}5=Hard{C_OFF})")
    return get_amount(prompt, 1, 5) - 1

def show_instructions():
    while True:
        print("Do you require instructions? [y|N]:", end="")
        response = str(input()).lower()
        if response != "y" and response != "n" and response !="":
            print("Enter 'Y' or 'N'.")
        else:
            break

    clear_screen()    

    # Do this as a guard condition/return to avoid unnecessary indentation of
    # instruction text, and maximize use of line-length under PEP8
    if response == "n": return
   
    print(
        f"{C_EMPH}Lunar Dome - Instructions:{C_OFF}\n\n"
        f"You are the overseer of an new colony living in an experimental "
        f"'{C_EMPH}Lunar Dome{C_OFF}'.\nYour job is to keep the colony "
        f"functioning for as long as possible.\n\n"
        f"{C_EMPH}Colonists{C_OFF} consume a certain number of units of "        
        f"{C_OXY}Oxygen{C_OFF} (to breathe) and {C_SOUP}Soup{C_OFF}\n(for "
        f"food/water) per year. On each turn, you must buy enough "
        f"{C_OXY}Oxygen{C_OFF} and {C_SOUP}Soup{C_OFF} to\nkeep all the "
        f"{C_EMPH}Colonists{C_OFF} alive.\n\n"
        f"The {C_INTEG}Integrity{C_OFF} of the {C_EMPH}Dome{C_OFF} is "
        f"reduced due to wear and tear proportional to the\nnumber of "
        f"{C_EMPH}Colonists{C_OFF} living in it. A maintenance charge is "
        f"assessed to restore\nthe {C_EMPH}Dome{C_OFF} to 100% "
        f"{C_INTEG}Integrity{C_OFF}. If you have insufficient "
        f"{C_EMPH}Credits{C_OFF} to cover this\ncharge, the "
        f"{C_INTEG}Integrity{C_OFF} of the {C_EMPH}Dome{C_OFF} will "
        f"continue to decline.\n\n"
        f"Beyond your initial budget, additional {C_EMPH}Credits{C_EMPH} can "
        f"be earned by using excess\n{C_OXY}Oxygen{C_OFF} to make, and sell, "
        f"'{C_SCULPT}Lunar Sculptures{C_OFF}'. Be careful not to use up ALL\n"
        f"your {C_OXY}Oxygen{C_OFF} and to keep enough for your "
        f"{C_EMPH}Colonists{C_OFF}!\n\n"
        f"{C_EMPH}NOTE:{C_OFF} The price of {C_OXY}Oxygen{C_OFF}, "
        f"{C_SOUP}Soup{C_OFF}, and the value of '{C_SCULPT}Lunar "
        f"Sculptures{C_OFF}' will\nfluctuate over time.  Buy low and sell high!"
        f"\n\n(Press [Enter] to continue ...)"
    )
    input()
    clear_screen()    
    print(
        f"{C_EMPH}Lunar Dome - Instructions:{C_OFF} (continued ...)\n\n"
        f"Random events ({C_BAD}'Calamities'{C_OFF}, which are {C_BAD}BAD,"
        f"{C_OFF} and {C_GOOD}'Boons'{C_OFF}, which are {C_GOOD}GOOD"
        f"{C_OFF} can\noccur that result in you {C_OFF} or "
        f"{C_SOUP}Soup{C_OFF}, or result in {C_BAD}damage{C_OFF}\nor "
        f"{C_GOOD}repairs{C_OFF} to the {C_INTEG}Integrity{C_OFF} of the "
        f"{C_EMPH}Dome{C_OFF}. If you let your {C_OXY}Oxygen{C_OFF} "
        f"stores, {C_SOUP}Soup{C_OFF}\nstocks or the {C_EMPH}Dome's{C_OFF} "
        f"{C_INTEG}Integrity{C_OFF} get too low, these events can be "
        f"significant\nenough to {C_BAD}end your game!{C_OFF}\n\n"
        f"If you lack enough {C_OXY}Oxygen{C_OFF} or {C_SOUP}Soup{C_OFF} "
        f"to sustain all the {C_EMPH}Colonists{C_OFF}, or the\n"
        f"{C_INTEG}Integrity{C_OFF} of the {C_EMPH}Dome{C_OFF} falls to "
        f"0, the colony is {C_BAD}no longer viable!{C_OFF} The "
        f"{C_EMPH}Dome{C_OFF}\nexperiment comes to an end, all the "
        f"{C_EMPH}Colonists{C_OFF} are returned to Earth, and ... \nthe "
        f"{C_BAD}GAME is OVER!{C_OFF}\n\n"
        f"{C_GOOD}GOOD LUCK!{C_OFF}\n\nPress [Enter] when ready.", end=""
    )
    input()  
    clear_screen()

# Run!
if __name__ == '__main__':
    lunardome() 