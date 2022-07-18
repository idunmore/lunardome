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
from sty import fg

# Constants
MAX_INTEGRITY = 100

# Multiplier for each difficulty "level"; higher numbers = harder.
DIFFICULTY_MULTIPLIER = [1, 1.25, 1.5, 1.75, 2.00]

class C():
    """
    Text color/effect aliases (from "sty" module values).
    Use with f-strings: "{C.Soup}Soup-colored text.{C.Off}
    """
    # C class = "Color"; Abbreviations are to reduce l
    Soup = fg.yellow        # Soup
    Emph = fg.white         # Emphasis
    Oxy = fg.li_blue        # Oxygen
    Sculpt = fg.magenta     # Lunar Sculptures
    Integ = fg.cyan         # Integrity
    Credit = fg.li_green    # Credit
    Good = fg.green         # Good/Boon
    Bad = fg.red            # Bad/Calamity
    Easy = fg.green         # Easy
    Hard = fg.red           # Hard
    Off = fg.rs             # Default Color (Color="OFF")

class CText():
    """
    Text with coloring/effects applied (shortcuts for f-string interpolation).
    """
    Soup = f"{C.Soup}Soup{C.Off}"
    Oxygen = f"{C.Oxy}Oxygen{C.Off}"
    Integrity = f"{C.Integ}Integrity{C.Off}"
    Sculptures = f"{C.Sculpt}Lunar Sculptures{C.Off}"
    Credits = f"{C.Credit}Credits{C.Off}"
    Colonists = f"{C.Emph}Colonists{C.Off}"

class EventType(Enum):
    """Inidcates if an Event is a BOON (good) or a CALAMITY (bad)."""
    BOON = 0
    CALAMITY = 1

class Commodity(Enum):
    """Indicates which type of Commodity is being referenced."""
    OXYGEN = 0
    SOUP = 1
    INTEGRITY = 2

class DomeState():
    """Represents, and manipulates, the entire state of the Dome/Colony."""
    def __init__(self, difficulty: int):
        self.__year = 0
        self.__difficulty = DIFFICULTY_MULTIPLIER[difficulty]
        # Starting values, and values that have a random element but are fixed
        # for the duration of a single game.
        self.__credits = int(5000 - 1000 * (self.__difficulty -1))    
        self.__colonists = 100
        self.__soup = 2000
        self.__oxygen = 3000
        self.__integrity = 100  
        self.__soup_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))        
        self.__oxygen_required_per_colonist = (
            random.randrange(2, 3 + int(self.__difficulty)))        
        self.__sculpture_cost = random.randrange(2, 3 + int(self.__difficulty))
        # Initialize these values at a Class level ...        
        self.__soup_cost = 0
        self.__oxygen_cost = 0        
        self.__sculpture_value = 0
        # ... and then update them at initialization, and every per turn:
        self.end_turn()       

    @property
    def year(self) -> int:
        """How long the Dome has been running (number of turns)."""
        return self.__year

    @property
    def credits(self) -> int:
        """Available credits."""
        return self.__credits

    @credits.setter
    def credits(self, value: int):
        """Available credits."""
        self.__credits = int(value) if value > 0 else 0

    @property
    def colonists(self) -> int:
        """Number of Colonists currently in the Dome."""
        return self.__colonists

    @property
    def soup_required_per_colonist(self) -> int:
        """Number of Soup units required per Colonist (per turn)."""
        return self.__soup_required_per_colonist

    @property
    def oxygen_required_per_colonist(self) -> int:
        """Number of Oxygen units required per Colonist (per turn)."""
        return self.__oxygen_required_per_colonist

    @property
    def sculpture_cost(self) -> int:
        """Number of Oxyen units it costs to make a Lunar Scuplture."""
        return self.__sculpture_cost

    @property
    def soup_cost(self) -> int:
        """Number of Credits required for one unit of Soup."""
        return self.__soup_cost

    @property
    def oxygen_cost(self) -> int:
        """Number of Credits required for one unit of Oyxgen."""
        return self.__oxygen_cost

    @property
    def sculpture_value(self) -> int:
        """Number of Credits gained by making/selling a Lunar Sculpture."""
        return self.__sculpture_value

    @property
    def difficulty(self) -> float:
        """Difficulty multiplier."""
        return self.__difficulty

    @property
    def soup(self) -> int:
        """Number of units of Soup in stock."""
        return int(self.__soup)
    
    @soup.setter
    def soup(self, value: int):
        """Number of units of Soup in stock."""
        self.__soup = int(value) if value > 0 else 0

    @property
    def oxygen(self) -> int:
        """Number of units of Oxygen in tanks."""
        return int(self.__oxygen)
    
    @oxygen.setter
    def oxygen(self, value: int):
        """Number of units of Oxygen in tanks."""
        self.__oxygen = int(value) if value > 0 else 0
        
    @property
    def integrity(self) -> int:
        """Integrity level of the Dome."""
        return int(self.__integrity)

    @integrity.setter
    def integrity(self, value: int):
        """Integrity level of the Dome."""
        if value > 0 and value <= 100:
            self.__integrity = int(value)
        elif value > 100:
            self.__integrity = 100
        else:
            self.__integrity = 0
       
    @property
    def maintenance_cost(self) -> int:
        """Cost to return Dome to 100% integrity."""
        return int((MAX_INTEGRITY - self.integrity) * self.difficulty) * 2

    @property
    def is_medium_or_lower_difficulty(self) -> bool:
        """Indicates if we're playing at mid-level or lower difficulty."""       
        return self.difficulty < (
            DIFFICULTY_MULTIPLIER[int(len(DIFFICULTY_MULTIPLIER)/2)])

    @property
    def is_viable(self) -> bool:
        """Indicates if the Dome/Colony is currently viable."""
        # If any commodity is exhausted, the dome is no longer viable.
        if self.oxygen <= 0 or self.soup <= 0 or self.integrity <= 0:
            return False     
        else:
            return True

    def display(self):
        """Displays the current state of the Dome/Colony."""
        clear_screen()
        print(f"There are {C.Emph}{self.colonists:,d}{C.Off} colonists "
            f"living in the dome, in year {C.Emph}{self.year:,d}{C.Off}.")      
        print(f"Available credits: {C.Credit}{self.credits:,d}{C.Off}.")
        print(f"Dome integrity is at {C.Integ}{self.integrity:,d}%{C.Off}; "
            f"annual maintenance is {C.Credit}{self.maintenance_cost:n}{C.Off} "
            f"credits.")            
        print(f"{CText.Soup} stocks stand at {C.Soup}{self.soup:,d}{C.Off} "
            f"units.")        
        print(f"Each colonist requires {C.Soup}"
            f"{self.soup_required_per_colonist:n}{C.Off} units of {CText.Soup} "
            f"per year, at {C.Credit}{self.soup_cost:n}{C.Off} credits "
            f"per unit.")
        if self.is_medium_or_lower_difficulty:
            soup_lasts = int((self.soup
                / (self.colonists * self.soup_required_per_colonist))) 
            print(f"Current {CText.Soup} stocks will last about "
              f"{C.Soup}{soup_lasts:n}{C.Off} years at present population.")
            soup_total_cost = (self.soup_cost
                * self.soup_required_per_colonist * self.colonists)         
            print(f"A one year supply of {CText.Soup} for all colonists "
                f"costs {C.Credit}{soup_total_cost:,d}{C.Off} credits.")            
        print(f"{CText.Oxygen} tanks currently hold {C.Oxy}{self.oxygen:,d}"
            f"{C.Off} units of {CText.Oxygen}.")
        print(f"Each colonist requires {C.Oxy}"
            f"{self.oxygen_required_per_colonist:n}{C.Off} units of "
            f"{CText.Oxygen} per year, at {C.Credit}{self.oxygen_cost:n}"
            f"{C.Off} credits per unit.")
        if self.is_medium_or_lower_difficulty:
            oxygen_lasts = int((self.oxygen
                / (self.oxygen_required_per_colonist * self.colonists)))
            print(f"Current {CText.Oxygen} stores will last about {C.Oxy}"
                f"{oxygen_lasts:n}{C.Off} years at present population.")
            oxygen_total_cost = (self.oxygen_cost
                * self.oxygen_required_per_colonist * self.colonists)
            print(f"A one year supply of {CText.Oxygen} for all colonists "
                f"costs {C.Credit}{oxygen_total_cost:,d}{C.Off} credits.")                  
        print(f"{CText.Sculptures} cost {C.Oxy}{self.sculpture_cost:n}{C.Off} "
            f"units of {CText.Oxygen} to make. They sell for {C.Credit}"
            f"{self.sculpture_value:n}{C.Off} credits.")        

    def end_turn(self):
        """Ends the current turn; updates all Dome state values accordingly."""
        # Soup, Oxygen, Sculpture prices vary every turn.        
        self.__soup_cost = random.randrange(3, 5 + int(self.__difficulty))
        self.__oxygen_cost = random.randrange(3, 5 + int(self.__difficulty))       
        self.__sculpture_value = (
            self.oxygen_cost * self.sculpture_cost + random.randrange(-2, 5))
        # Integrity and population change every turn AFTER the first year;
        # integrity reduces by percentage of colonists and colony grows.
        if self.year != 0:
            self.soup -= int(self.colonists * self.soup_required_per_colonist)
            self.oxygen -= int(
                self.colonists * self.oxygen_required_per_colonist)
            self.integrity -= int(self.colonists / 10)
            # Update colonists LAST, so as not to skew calcs for CURRENT year.
            # Colony increases by PERCENTAGE, to simulate accelerating growth.
            modifier = int(self.difficulty) * 10          
            increase_percent = 1 + random.randrange(1, modifier) / 100                 
            self.__colonists = int(self.colonists * increase_percent)           
            
        self.__year += 1

    def perform_maintenance(self):
        """
        Applies maintenance costs to restore Integrity to 100%, if possible.
        Otherwise outputs appropriate message on Dome and Credit state.
        """
        if self.integrity == 100:
            print(f"{fg.green}No dome maintenance required this year.{fg.rs}")
        elif self.credits >= self.maintenance_cost:
            print(f"Dome {fg.green}repaired{fg.rs} for "
                f"{fg.green}{self.maintenance_cost:,d}{fg.rs} credits; now at "
                f"{C.Integ}100% {CText.Integrity}.")
            self.credits -= self.maintenance_cost
            self.integrity = 100            
        else:
            print(f"{fg.red}Insufficient credits to repair dome!{fg.rs}")    

class Event():
    """Base class for creating BOON or CALAMITY events."""
    def __init__(
        self, event_type: EventType,
        commodity:Commodity,
        minimum:int,
        maximum: int,
        message: str
    ):
        self.__event_type = event_type
        self.__commodity = commodity
        self.__minimum = minimum
        self.__maximum = maximum
        self.__message = message
        self.__amount = 0
        
    def apply_event(self, dome_state:DomeState):
        """Applies the effects of an event to the state of the Dome."""
        # Amount is a random value, in a specified range.  For "calamaties",
        # this is then adjusted by a difficulty modifier.  Sign is set depending
        # on whether it is a Calamity (-) or a Boon (+).
        value = random.randrange(self.__minimum, self.__maximum)
        if self.__event_type == EventType.BOON:
            self.__amount = value
        else:
            self.__amount = -abs(value * dome_state.difficulty)        

        # Adjust the appropriate Dome State commodity; since we're using
        # signed amounts we can simply ADD the value.
        match self.__commodity:
            case Commodity.OXYGEN:
                dome_state.oxygen += self.__amount                
            case Commodity.SOUP:
                dome_state.soup += self.__amount                
            case Commodity.INTEGRITY:
                dome_state.integrity += self.__amount                

        self.__display()

    def __display(self):
        """Displays the event and its effects."""
        # Display BOONs as "Good", CALAMITIES as "Bad"       
        color = C.Good if self.__event_type == EventType.BOON else C.Bad
        print(f"\n{color}{self.__message.format(units=abs(self.__amount))}"
            f"{C.Off}")              

# Calamity and Boon Events:

# Adding a new Calamity or Boon simply requires creating a new class, derived
# from "Event", that calls the super class initializer with appropriate values
# and then adding it to the events[] array in the "lunar_dome" function.
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
def lunar_dome():
    """Main Game Loop."""

    # Add Event-derived Boons or Calamities to the events[] list.  If you want
    # and event to occur more frequently, add it multiple timesm.
    events = [
        SoupDragon(), MeteorStrike(), MoonQuake(), IronChicken(), SoupGeyser(),
        Astronaut()
    ]
    
    # Show title/intro, and show instructions if required.
    show_title()
    show_instructions()

    # Replay Game Loop
    while True:
        # Get desired difficulty level, and setup Dome accordingly.
        difficulty = choose_difficulty()  
        dome = DomeState(difficulty)   

        # Main game loop:
        while dome.is_viable:
            dome.display()        
            random_event(events, dome)
            print()        
            buy_commodity(Commodity.OXYGEN, dome)
            buy_commodity(Commodity.SOUP, dome)
            make_scupltures(dome)    
            dome.perform_maintenance()        
            dome.end_turn()
            print()
            enter_to_continue("for next turn.")        

        # Game Over ...
        game_over(dome)

        # Play again?
        if not get_yes_or_no("Play again?"): break

def buy_commodity(commodity: Commodity, dome_state: DomeState):
    """Prompts to buy a specified Commodity and updates Dome state as needed."""
    match commodity:
        case Commodity.OXYGEN:
            can_afford = int(dome_state.credits/dome_state.oxygen_cost)
            commodity_name = CText.Oxygen
            cost_per_unit = dome_state.oxygen_cost              
        case Commodity.SOUP:
            can_afford = int(dome_state.credits/dome_state.soup_cost)
            commodity_name = CText.Soup
            cost_per_unit = dome_state.soup_cost         
        case Commodity.INTEGRITY:
            sys.exit("Cannot buy Integrity; Error in main gaim loop Logic.") 
    
    prompt = f"How many units of {commodity_name} do you want to buy?"
    units = get_amount(prompt, 0, can_afford)
    
    # Apply results of Purchase
    print(f"You bought {C.Emph}{units:n}{C.Off} units of {commodity_name} for "
        f"a total of {C.Credit}{units * cost_per_unit:n}{C.Off} credits.")

    # Update purchased commodity value
    if commodity == Commodity.OXYGEN:
        dome_state.oxygen += units
    else:
        dome_state.soup += units

    # Update credits
    dome_state.credits -= units * cost_per_unit
    print(f"You have {C.Credit}{dome_state.credits:n}{C.Off} credits "
        "remaining.")

def make_scupltures(dome_state: DomeState):
    """Prompts to make Lunar Sculptures, and updates Dome state as needed."""
    prompt = (f"How many {C.Sculpt}Lunar Sculptures{C.Off} do you want to make "
        "and sell?")
    can_afford = int(dome_state.oxygen / dome_state.sculpture_cost)
    sculptures = get_amount(prompt, 0, can_afford)
    sculpture_profit = dome_state.sculpture_value * sculptures
    sculpture_oxygen_usage = sculptures * dome_state.sculpture_cost
    print(f"You made {C.Credit}{sculpture_profit:,d}{C.Off} credits selling "
        f"{CText.Sculptures}, consuming {C.Emph}"
        f"{sculpture_oxygen_usage}{C.Off} units of {CText.Oxygen}.")
    
    # Update oxygen used and credits earned    
    dome_state.oxygen -= sculpture_oxygen_usage     
    dome_state.credits +=  sculpture_profit

def random_event(events: list[Event], dome_state: DomeState):
    """Determines if a Random Event occurs, and applies it if so."""
    # Events at an average rate of 1 turn in 10
    if random.randrange(0, 100) % 10 == 0:
        # Pick a random event and apply it ..
        events[random.randrange(0, len(events) - 1)].apply_event(dome_state)
        print("")

def get_amount(prompt: str, minimum: int, maximum: int) -> int:
    """
    Prompts the user, with the supplied prompt text, to enter an amount between
    the specified minimum and maximum values.
    """
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

def get_yes_or_no(prompt: str) -> bool:
    """Prompts for a Yes/No (Y/N) response; returns True if YES."""
    while True:
        print(f"{prompt} [Y|N]:", end="")
        response = str(input()).lower()
        if response != "y" and response != "n" and response !="":
            print("Enter 'Y' for 'Yes' or 'N' for 'No'.")
        else:
            break

    return bool if response =="y" else False

def enter_to_continue(prompt: str):
    """Prompts to 'Press [Enter]' with custom message; returns on [Enter]"""
    print(f"(Press [Enter] {prompt})", end="")
    input()

def game_over(dome: DomeState):
    """Displays Game Over notification."""
    clear_screen()
    print(f"{C.Bad}GAME OVER!{C.Off}\n")
    if dome.oxygen <= 0:
        commodity = f"{CText.Oxygen} stores"
    elif dome.soup <= 0:        
        commodity = f"{CText.Soup} stocks"
    else:
        commodity = CText.Integrity

    print(f"You allowed the {C.Emph}Dome's{C.Off} {commodity} to reach {C.Bad}"
        f"0{C.Off}!\n\nThis is insufficient to sustain the colony; all "
        f"colonists have been returned to\nEarth, and the {C.Emph}Dome{C.Off} "
        f"experiment has ended.\n")

    print(f"You kept the colony viable for {C.Good}{dome.year:n}{C.Off} years, "
        f"and the colony grew to {C.Emph}{dome.colonists:n}{C.Off} "
        f"{CText.Colonists}.\n")

def clear_screen():
    """Clear the console/terminal, while preserving command buffer."""
    _ = os.system("cls" if os.name=="nt" else "clear")

def show_title():
    """Displays the Title/Introducton."""
    pass

def choose_difficulty() -> int:
    """Prompts the user to choose a difficulty level."""
    clear_screen()    
    print(f"{C.Emph}Lunar Dome - Choose Difficulty Level:{C.Off}\n\n"
        f"{C.Emph}Lunar Dome{C.Off} offers {C.Emph}five{C.Off} levels of "
        f"progressive difficulty with {C.Easy}1{C.Off} being the {C.Easy}"
        f"easiest{C.Off}\nand {C.Hard}5{C.Off} the {C.Hard}hardest{C.Off}.\n\n"
        f"At higher difficulty levels, there is:\n\n"
        f" * More variation in the cost/value for {CText.Oxygen}, "
        f"{CText.Soup} and {CText.Sculptures}.\n"
        f" * A reduction in the number of starting {CText.Credits}.\n"
        f" * An increase in how fast the population of the colony grows.\n"
        f" * An increase in the negative impact of {C.Bad}Calamities{C.Off} "
        f"vs. {C.Good}Boons{C.Off}.\n"
        f" * Elimination of low-commodity warnings and estimates.\n"
    )

    prompt = (
        f"Enter Difficulty ({C.Easy}1=Easy{C.Off}, {C.Hard}5=Hard{C.Off})")
    return get_amount(prompt, 1, 5) - 1

def show_instructions():
    """Asks the user if they need instructions; displays them if Yes."""
    response = get_yes_or_no("Do you require instructions?")
    clear_screen()    
    if response == False: return
   
    print(
        f"{C.Emph}Lunar Dome - Instructions:{C.Off}\n\n"
        f"You are the overseer of an new colony living in an experimental "
        f"'{C.Emph}Lunar Dome{C.Off}'.\nYour job is to keep the colony "
        f"functioning for as long as possible.\n\n"
        f"{CText.Colonists} consume a certain number of units of "        
        f"{CText.Oxygen} (to breathe) and {CText.Soup}\n(for food/water) per "
        f"year. On each turn, you must buy enough {CText.Oxygen} and "
        f"{CText.Soup} to\nkeep all the {CText.Colonists} alive.\n\n"
        f"The {CText.Integrity} of the {C.Emph}Dome{C.Off} is "
        f"reduced due to wear and tear proportional to the\nnumber of "
        f"{CText.Colonists} living in it. A maintenance charge is "
        f"assessed to restore\nthe {C.Emph}Dome{C.Off} to 100% "
        f"{CText.Integrity}. If you have insufficient {CText.Credits} to cover "
        f"this\ncharge, the {CText.Integrity} of the {C.Emph}Dome{C.Off} will "
        f"continue to decline.\n\n"
        f"Beyond your initial budget, additional {CText.Credits} can "
        f"be earned by using excess\n{CText.Oxygen} to make, and sell, "
        f"'{CText.Sculptures}'. Be careful not to use up ALL\nyour "
        f"{CText.Oxygen} and to keep enough for your {CText.Colonists}!\n\n"        
        f"{C.Emph}NOTE:{C.Off} The price of {CText.Oxygen}, {CText.Soup}, "
        f"and the value of '{CText.Sculptures}' will\nfluctuate over time. "
        f"Buy low and sell high!\n"        
    )
    enter_to_continue("to continue ...")
    clear_screen()    
    print(
        f"{C.Emph}Lunar Dome - Instructions:{C.Off} (continued ...)\n\n"
        f"Random events ({C.Bad}'Calamities'{C.Off}, which are {C.Bad}BAD,"
        f"{C.Off} and {C.Good}'Boons'{C.Off}, which are {C.Good}GOOD"
        f"{C.Off} can\noccur that result in you {C.Good}gaining{C.Off} or "
        f"{C.Bad}losing {CText.Oxygen} or {CText.Soup}, or result in {C.Bad}"
        f"damage{C.Off}\nor {C.Good}repairs{C.Off} to the {CText.Integrity} "
        f"of the {C.Emph}Dome{C.Off}. If you let your {CText.Oxygen} "
        f"stores, {CText.Soup}\nstocks or the {C.Emph}Dome's{C.Off} "
        f"{CText.Integrity} get too low, these events can be "
        f"significant\nenough to {C.Bad}end your game!{C.Off}\n\n"
        f"If you lack enough {CText.Oxygen} or {CText.Soup} "
        f"to sustain all the {CText.Colonists}, or the {CText.Integrity}\nof "
        f"the {C.Emph}Dome{C.Off} falls to 0, the colony is {C.Bad}no longer "
        f"viable!{C.Off} The {C.Emph}Dome{C.Off} experiment\ncomes to an end, "
        f"all the {CText.Colonists} are returned to Earth, and ... \nthe "
        f"{C.Bad}GAME is OVER!{C.Off}\n\n"
        f"{C.Good}GOOD LUCK!{C.Off}\n"
    )
    enter_to_continue("when ready.")
    clear_screen()

# Run!
if __name__ == '__main__':
    lunar_dome() 