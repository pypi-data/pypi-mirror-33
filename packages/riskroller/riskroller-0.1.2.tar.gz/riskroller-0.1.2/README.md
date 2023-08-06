

# Background

Python challenge

There are three questions. Submit solutions and test cases for each. When we review code, we care equally about clarity and correctness. If you get stuck, don't worry--just write a sentence or two about where you got stuck and why.


# This challenge - Risk

a. 

The board game Risk has simple combat rules: an invading force of 1 to 3 units attacks a defending force of 1 to 3 units. Each invading unit rolls a 6-sided die, and each defending unit rolls a 6-sided die. The highest numbered invading die matches to the highest numbered defending die, then the next highest, etc., as long as there are two dice to match up. For example, if there are two attacking dice and one defending die, only one from each side match up. The side with the higher number on each match up wins, with the defending die winning the tie.

Write a function that returns a fair, random `(invading_wins, defending_wins)` for an input `(invading_count, defending_count)`:

```
def random_outcome(invading_count, defending_count):
  # ...
  return (invading_wins, defending_wins)
``` 

Example cases are below.

```
random_outcome(2, 1) == (1, 0)
random_outcome(2, 1) == (0, 1)
random_outcome(2, 2) == (1, 1)
random_outcome(2, 2) == (0, 2)
random_outcome(2, 2) == (2, 0)
random_outcome(3, 1) == (1, 0)
random_outcome(3, 1) == (0, 1)
```

b. 

Using this function, write a script that prints a good estimate for the probabiltiy of the invader winning at least one for each of the 9 cases of 1..3 invaders and 1..3 defenders. Averaging the result of 1000 evaluations for the same input is good enough estimate of the outcome.

Example output is below.

```
with 1 invader and 1 defender, the probably of the invader winning at least one is about 41%
```
