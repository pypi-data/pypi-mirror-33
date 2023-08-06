"""Battle via dice."""

# imports
import random  # Requirement was random num generator, assuming pseudorandom
import argparse
from map import map

# globals
dice = [1, 2, 3, 4, 5, 6]
forces = [1, 2, 3]
__version__ = "0.1.3"

# arguments
parser = argparse.ArgumentParser(description='one round of risk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--randommode', action='store_true', help='Randomly selects number of rolls for invaders and defenders for round.')
parser.add_argument('-n', '--no-logo', dest='logo_off', help='disables printing logo', action='store_true', default=False)
parser.add_argument('-v', '--verbose', help='print more stuff', action='store_true')
parser.add_argument('-i', '--inputmode', action='store_true', help="Manually input number of rolls available to invader and defender.")
parser.add_argument('-e', '--evaluatemode', action="store_true", help="Displays probability and selects random pairing of dice rolls for invader and defender.")
args = parser.parse_args()

# functions


def evaluations(number_of_rounds):
    """Evaluate outcome probability of rolls available."""
    global forces
    if args.verbose:
        print('You selected evaluations mode and number of rounds is 1000.\n')
    i = 0
    invaders_win = 0
    defenders_win = 0
    invaders = random.choice(forces)
    defenders = random.choice(forces)
    while i < number_of_rounds:
        invaders_rolls = roll_it(invaders)
        defenders_rolls = roll_it(defenders)
        total_invader_wins, total_defender_wins = evaluate_rolls(invaders_rolls, defenders_rolls)
        invaders_win = invaders_win + total_invader_wins
        defenders_win = defenders_win + total_defender_wins
        i = i + 1
    invaderspercentage = invaders_win/(invaders_win+defenders_win)
    defenderspercentage = defenders_win/(invaders_win+defenders_win)
    print(f'Invaders rolls: {invaders}\nDefenders rolls: {defenders}\nRounds: {number_of_rounds}\n')
    print(f'Invaders wins: {invaders_win} percentage: {invaderspercentage}')
    print(f'Defenders wins: {defenders_win} percentage: {defenderspercentage}')
    exit()


def check_mode():
    """Check to ensure user selected a mode."""
    if not args.randommode and not args.inputmode and not args.evaluatemode:
        print('no mode selected, use -i or -r or -e')
        exit('goodbye')


def roll_it(team):
    """Roll virtual dice as many times as size of force."""
    i = 0
    teams_rolls = []
    while i < team:
        roll = random.choice(dice)
        teams_rolls.append(int(roll))
        i = i + 1  # I prefer to be explicit with my iterators 
    return teams_rolls


def get_input():
    """Input mode, user sets invader count and defender count."""
    invaders = input('\033[92mHow many invaders (1,2, or 3)?:\033[0m ')
    defenders = input('\033[92mHow many defenders (1,2, or 3)?:\033[0m ')
    if args.verbose:
        print(f"\n\033[94mOk, The following is set:\033[0m\n\n\033[93minvaders: \033[0m{invaders}\n\033[92mdefenders: \033[0m{defenders}\n")
    return int(invaders), int(defenders)


def evaluate_rolls(invaders, defenders):
    """Evaluate winners and losers from rolls."""
    invaders.sort(reverse=True)
    defenders.sort(reverse=True)
    invaderwins = [item1 for item1, item2 in zip(invaders, defenders) if item1 > item2]
    defenderwins = [item1 for item1, item2 in zip(defenders, invaders) if item1 > item2]
    defenderties = [item1 for item1, item2 in zip(defenders, invaders) if item1 == item2]
    total_invader_wins = len(invaderwins)
    total_defender_wins = len(defenderwins) + len(defenderties)
    if args.verbose:
        print(f'invader win list: {invaderwins}')
        print(f'defender win list: {defenderwins}')
        print(f'defender tie list: {defenderties}')
    return total_invader_wins, total_defender_wins


def play_again():
    """Check if user wants to play again."""
    get_input = input('\nPlay again? (y/n): ')
    if get_input == 'y':
        from subprocess import call
        call("clear")
        # start again
        main()
    else:
        exit('Thanks for playing!')


def main():
    """Plays a round of risk for two teams based on criteria."""
    if not args.logo_off:
        print(map)
    # make sure the user set a mode or ask them to and run again
    check_mode()
    # based on the mode, get the invaders count and defenders count
    if args.inputmode:
        invaders, defenders = get_input()
    if args.evaluatemode:
        evaluations(1000)
    else:
        if args.randommode:
            invaders = random.choice(forces)
            defenders = random.choice(forces)
    # roll dice for each and store in list
    invaders_rolls = roll_it(invaders)
    defenders_rolls = roll_it(defenders)
    if args.verbose:
        print(f'Invader rolls: {invaders_rolls}\nDefender rolls: {defenders_rolls}')
    invader_wins, defender_wins = evaluate_rolls(invaders_rolls, defenders_rolls)
    print(f'Invader wins: {invader_wins}\nDefender wins: {defender_wins}\n')
    play_again()


if __name__ == '__main__':
    main()
