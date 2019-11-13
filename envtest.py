import main
from random import choice

possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

main.make()

for episode in range(10000):
    print("Episode: ", episode)
    obs = main.reset()
    for t in range(6000):
        #actions = [[1, 0, 0], [0, 1, 0]]
        actions = [choice(possible_actions), choice(possible_actions)]
        obs, reward, done, info = main.step(actions)
        if done:
            print("Episode finished")
            break

print("ALL DONE")
