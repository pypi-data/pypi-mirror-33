from .command import Command
import getch
import random
import sys

class Play(Command):
    def usage(self):
        return """
usage: rock play

Play a game of {rock,paper,scissors}
        """

    def go(self):
        if not sys.stdin.isatty():
            self.lprint(0,'No cheating!')
            return 0
        choices = {'r': 'rock', 'p': 'paper', 's': 'scissors'}
        wins = 0
        losses = 0
        ties = 0
        while True:
            c = random.choice(list(choices.keys()))
            self.lprint(0,
                "Enter 'r' for rock, 'p' for paper, 's' for scissors "
                    "or 'q' to quit: ",
                end=" "),
            sys.stdout.flush()
            u = getch.getche()
            self.lprint(0)
            if u == 'q':
                self.lprint(0)
                break
            if u == c:
                self.lprint(0, "Tie! We both guessed '%s' " % choices[u])
                ties += 1
                continue
            if ((u == 'r' and c == 's') or
                (u == 'p' and c == 'r') or
                (u == 's' and c == 'p')):
                wins += 1
                self.lprint(0, 'You win! (%s >> %s)'
                    % (choices[u], choices[c]))
            else:
                losses += 1
                self.lprint(0, 'You lose! (%s << %s)'
                    % (choices.get(u), choices[c]))
        self.lprint(0,'Your score summary: %d wins, %d ties and %d losses'
            % (wins, ties, losses))
        return 0
