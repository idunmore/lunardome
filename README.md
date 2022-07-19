# Lunar Dome 
## A simple "Lunar Dome" management game.

### Origins & Inspiration
The very first version of this game was something I wrote for the Atari 800, in Atari Basic, in 1979.  That was a simpler affair, and was based on a medieval "Kingdom" style game played over a [tele-printer](https://en.wikipedia.org/wiki/Teleprinter) interface to the local college computer.

The next version I did, a couple or three years later, and also on the Atari 800, was inspired by a game called "Dome Dweller" written by Tim Hartnell, published in "[The Book of Listings](http://bbcmicro.co.uk/game.php?id=3169)", and later described in "[Games for Your Atari](https://atariage.com/forums/topic/292136-games-for-your-atari-book/)".

### This Version
As part of the "completeness" factor (see "Why write a game like this today?", I wanted to add a couple of features over the last version I wrote (some 40 years ago, now):

* Adds random "Boon" (good) and "Calamity" (bad) events.  These add interest, and some additional risk if the player is min/maxing their gameplay.

	* They add some minor "[Clangers](https://en.wikipedia.org/wiki/Clangers)" theming ...
	
	* As a bonus, these are trivially extensible.	

* Add the "Integrity" of the Dome, not just as a recurring charge, but also as potential game-ending condition.

* Colorized text/context.

## Game Instructions

You are the overseer of an new colony living in an experimental 'Lunar Dome'.
Your job is to keep the colony functioning for as long as possible.

Colonists consume a certain number of units of Oxygen (to breathe) and Soup (for food/water) per year. On each turn, you must buy enough Oxygen and Soup to keep all the Colonists alive.

The Integrity of the Dome is reduced due to wear and tear proportional to the number of Colonists living in it. A maintenance charge is assessed to restore the Dome to 100% Integrity. If you have insufficient Credits to cover this charge, the Integrity of the Dome will continue to decline.

Beyond your initial budget, additional Credits can be earned by using excess Oxygen to make, and sell, 'Lunar Sculptures'. Be careful not to use up ALL your Oxygen and to keep enough for your Colonists!

NOTE: The price of Oxygen, Soup, and the value of 'Lunar Sculptures' will fluctuate over time. Buy low and sell high!

Random events ('Calamities', which are BAD, and 'Boons', which are GOOD can occur that result in you gaining or losing Oxygen or Soup, or result in damage or repairs to the Integrity of the Dome. If you let your Oxygen stores, Soup stocks or the Dome's Integrity get too low, these events can be significant
enough to end your game!

If you lack enough Oxygen or Soup to sustain all the Colonists, or the Integrity of the Dome falls to 0, the colony is no longer viable! The Dome experiment comes to an end, all the Colonists are returned to Earth, and ... the GAME is OVER!

GOOD LUCK!

## Why write a game like this today?
In my spare time, I've been mentoring a few prospective software engineers.  I wanted to set them a reasonably achievable goal that offered a simple, quickly achievable, way to bring together a number of concepts, including:

* **Object Orientation** - Specifically inheritance, polymorphism and encapsulation.
* **Extensibility** - Build something that could be trivially, quickly and reliably extended/modified.
* **Maintainability** - Singles points of change, where possible.
* **Trade-Offs in Typing** - How typing/type hints, or lack thereof, can impact code comprehension and subtle bugs, and how they work in modern Python
* **Coding Conventions** - Both to apply them consistently, and to see how they can be detrimental to readability, in some cases, when followed to the letter.
* **Lucid/Expressive Coding** - Illustrate the trade-offs in lucid/expressive or "self-documenting" code, vs. more terse/compact approaches.

I also wanted something that allowed my mentees the opportunity to "do something extra", in essence to get an idea of how they viewed/approached software development and their relative passion for it:

* This game can be implemented in **much** simpler manner, but with trade-offs as to how easy it is to extend or maintain, or what features it exhibits.

* The opportunity to be creative; adding gameplay features etc.

* Completeness; things like intro screens, embedded instructions, text coloration and multiple difficulty levels are not strictly required (my first version didn't have them).

Since it is not fair to assess someone else on a task one is not willing to undertake themselves, I needed to create my own version as a point of comparison and/or illustration.

Finally, this was a good opportunity to continue evaluating some "mobile programming" options.  I wrote this using an 11" iPad Pro (and Magic Keyboard), *while traveling*, using a combination of "[Replit](https://replit.com)", GitHub "[CodeSpaces](https://github.com/features/codespaces)" and "[Pythonista 3](https://apps.apple.com/us/app/pythonista-3/id1085978097)".

## Implementation Notes
#### Code is in Python 3.10.5:
* No reason to start new projects on older versions of the language.
* Allows usage of the new "match" functionality

#### Single Dependency:

* I used the "[sty](https://pypi.org/project/sty/)" module as a much easier way to add colorized terminal output than manually wrangling ANSI codes across platform.

* "sty" has **no dependencies** itself.

* All references to "sty" styling codes are abstracted, so can be easily replaced, in a single point in the code, if the dependency becomes and issue or there's a desire/need to remove it.

* The way "sty" is implemented allows it to be readily applied in f-strings (string literal interpolation).

#### Extensibility:

Extensibility is addressed as follows:

1. A trivial way to add new "Boon" or "Calamity" events.
2. A trivial way to adjust the difficulty of each "level".

##### Adding a new Boon or Calamity:

This simply requires deriving a new class from "Event", setting the appropriating initialization values, and adding an instance of the new event to the "events[]" array in the "lunar_dome" function.

The "Event" base/superclass takes care of display of the event details, calculating the effect, accommodating difficultly level and applying the effect to the state of the dome/colony.

As a simple example, we can create a new Calamity (disadvantage) by implementing a new class, derived from "Event":

    class CometImpact(Event):
	    def __init__(self):
		    super().__init__(EventType.CALAMITY, Commodity.INTEGRITY, 30, 70,
		    "A comet strikes the moon; Dome Integrity is reduced by {units:,d}!")
		    
And then adding this new event class to the list of events, in the "lunar_dome()" function, that can occur:

    events = [SoupDragon(), MeteorStrike(), MoonQuake(), IronChicken(), SoupGeyser(),    
	    Astronaut(), CometImpact()    
    ]

##### Adjusting Difficulty:

Difficulty is controlled by a "level" setting, which acts as an index into an array/list of "multipliers".  These multipliers are used to modify changes to certain values during turn-updates:

    DIFFICULTY_MULTIPLIER = [1, 1.25, 1.5, 1.75, 2.00]

If you wanted a different difficulty progression you could change the values as such:

    DIFFICULTY_MULTIPLIER = [1, 2, 3, 4, 5]

#### Maintainability:

Items that are likely to change are abstracted/have singles-points of change.  For example, changing the color used to indicate any specific commodity or value can be changed in ONE place, the "C" class.

#### Lucid/Expressive Code:

While it presents challenges with complying with the line-length limits prescribed by the PEP8 coding conventions, the following elements of lucid/expressive (aka "self-documenting" code are observed):

* Variable names/properties are detailed and explicit.

* Method/function names  are detailed and explicit; reading the main "game loop" should be extremely clear and easy to follow.

* Classes (objects) are encapsulated and fully responsible for their own integrity and behavior.
