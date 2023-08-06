from argparse import ArgumentParser
from .game import game
from .players import (
    HumanPlayer,
    NondeterministicAIPlayer,
    EnumerativeAIPlayer,
    TrainedAIPlayer,
)

player_choices = {
    "human": HumanPlayer,
    "brute_force": EnumerativeAIPlayer,
    "trained": TrainedAIPlayer,
    "random": NondeterministicAIPlayer,
}

parser = ArgumentParser()
parser.add_argument("player1", help="Type of player 1", choices=player_choices)
parser.add_argument("player2", help="Type of player 2", choices=player_choices)
parser.add_argument("--name1", help="Optional name for player 1")
parser.add_argument("--name2", help="Optional name for player 2")
parser.add_argument(
    "--debug", help="Enable debug mode (more verbose output)", action="store_true"
)
parser.add_argument(
    "--no-gui", help="Print very little to the screen", action="store_false"
)
args = parser.parse_args()


def main():
    if not args.no_gui:
        print("Running command-line game with no GUI")
    players = (
        player_choices[args.player1](name=args.name1),
        player_choices[args.player2](name=args.name2),
    )
    outcome, _, _, _ = game(players, debug=args.debug, gui=args.no_gui)
    # we don't need any of the other return values here
    # they are used for training though
    print("Final score")
    print("{2}: {0}, {3}: {1}", *outcome, *players)


if __name__ == "__main__":
    main()
