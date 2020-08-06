from collections import namedtuple
import csv

Game = namedtuple('Game', ['team1', 'team2'])
Team = namedtuple('Team', ['name', 'region', 'seed', 'bpi', 'adjEM', 'prob_rd_1', 'prob_rd_2', 'prob_rd_3', 'prob_rd_4', 'prob_rd_5', 'prob_rd_6'])
Node = namedtuple("Node", ['bracket', 'hn', 'fn', 'gn', 'parent', 'south', 'east', 'west', 'midwest', 'depth'])


def gen_state(bracket, bin_index):
    winners = []
    state = []
    for i in range(0, len(bracket)):
        winners.append(bracket[i][int(bin_index[i])])

    for i in range(0, len(winners)-1, 2):
        game = Game(winners[i], winners[i+1])
        state.append(game)

    return state


def gen_states(bracket):
    length = len(bracket)
    holder = "{0:{fill}" + str(length) + "b}"
    states = []
    if length >= 8:
        for i in range(0, 6 * length):
            bin_index = holder.format(i, fill='0')
            state = gen_state(bracket, bin_index)
            states.append(state)
    else:
        for i in range(0, 2 ** length):
            bin_index = holder.format(i, fill='0')
            state = gen_state(bracket, bin_index)
            states.append(state)

    return states


def fitness_function(bracket, fit_element):
    count = 0
    prob = 0
    for i in range(0, len(bracket)):
            prob += float(bracket[i][0][fit_element])
            prob += float(bracket[i][1][fit_element])
            count += 2

    if count == 0:
        count = 1

    return prob / count

#Use This to Update frontier
def update_frontier(frontier, parent, south_bracket, east_bracket, west_bracket, mid_west_bracket, fit_index):

    length = len(south_bracket)
    count = 0
    print(length)
    for i in range(0, length):
        for j in range(0, length):
            for k in range(0, length):
                for m in range(0, length):
                    count += 1
                    bracket = []
                    bracket.extend(south_bracket[i])
                    bracket.extend(east_bracket[j])
                    bracket.extend(west_bracket[k])
                    bracket.extend(mid_west_bracket[m])
                    fn = fitness_function(bracket, fit_index)
                    gn = (len(bracket)/2) + parent.gn
                    hn = fn + gn
                    new_node = Node(bracket, hn, fn, gn, parent, south_bracket[i], east_bracket[j], west_bracket[k], mid_west_bracket[m], parent.depth+1)
                    frontier.append(new_node)

    return frontier

def fill_team_regions(all_teams):
    south_teams = []
    east_teams = []
    west_teams = []
    mid_west_teams = []

    for i in range (0,len(all_teams)):
        if all_teams[i][1] == 'South':
            south_teams.append(all_teams[i])
        elif all_teams[i][1] == 'East':
            east_teams.append(all_teams[i])
        elif all_teams[i][1] == 'West':
            west_teams.append(all_teams[i])
        else:
            mid_west_teams.append(all_teams[i])

    sorted(south_teams, key=lambda x: x[1])
    sorted(east_teams, key=lambda x: x[1])
    sorted(west_teams, key=lambda x: x[1])
    sorted(mid_west_teams, key=lambda x: x[1])

    return south_teams, east_teams, west_teams, mid_west_teams

def fill_region_bracket(teams):
    games_bracket = []

    game1 = Game(teams[0], teams[15])
    game2 = Game(teams[7], teams[8])

    game3 = Game(teams[4], teams[11])
    game4 = Game(teams[3], teams[12])

    game5 = Game(teams[5], teams[10])
    game6 = Game(teams[2], teams[13])

    game7 = Game(teams[6], teams[9])
    game8 = Game(teams[1], teams[14])

    games_bracket.append(game1)
    games_bracket.append(game2)
    games_bracket.append(game3)
    games_bracket.append(game4)
    games_bracket.append(game5)
    games_bracket.append(game6)
    games_bracket.append(game7)
    games_bracket.append(game8)

    return games_bracket


def generate_root(south, east, west, mid_west):
    bracket = []
    bracket.extend(south)
    bracket.extend(east)
    bracket.extend(west)
    bracket.extend(mid_west)
    fn = fitness_function(bracket, 3)
    gn = (len(bracket) / 2) / 127
    hn = fn + gn
    root = Node(bracket, hn, fn, gn, None, south, east, west, mid_west, 0)
    return root


def a_star_bpi(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node.bracket) == 2:
            finals = gen_states(curr_node.bracket)

            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], 3)
                gn = ((len(finals) / 2) / 63) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], 3)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, 3)
            frontier.sort(key=lambda x: x[1])

        curr_node = frontier.pop()
    print('Num Steps:', steps)
    return curr_node

def a_star_adjEM(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node.bracket) == 2:
            finals = gen_states(curr_node.bracket)

            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], 4)
                gn = (len(finals) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], 4)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, 4)
            frontier.sort(key=lambda x: x[1])

        curr_node = frontier.pop()
    print('Num Steps:', steps)
    return curr_node

def a_star_538(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node.bracket) == 2:
            finals = gen_states(curr_node.bracket)

            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], parent.depth + 5)
                gn = (len(finals) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], parent.depth + 5)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, parent.depth + 5)
            frontier.sort(key=lambda x: x[1])

        curr_node = frontier.pop()
    print('Num Steps:', steps)
    return curr_node


def greedy_bpi(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node.bracket) == 2:
            finals = gen_states(curr_node.bracket)

            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], 3)
                gn = ((len(finals) / 2) / 63) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], 3)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, 3)
            frontier.sort(key=lambda x: x[2])

        curr_node = frontier.pop()
    print('Num Steps:', steps)

    return curr_node

def greedy_adjEM(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node.bracket) == 2:
            finals = gen_states(curr_node.bracket)

            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], 4)
                gn = (len(finals) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], 4)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, 4)
            frontier.sort(key=lambda x: x[2])

        curr_node = frontier.pop()
    print('Num Steps:', steps)
    return curr_node

def greedy_538(root):
    frontier = []
    curr_node = root
    frontier.append(root)
    steps = 0
    while len(curr_node.bracket) > 1 or len(frontier) == 0:
        steps += 1
        parent = curr_node

        if len(curr_node) == 2:
            finals = curr_node.bracket
            for i in range(0, len(finals)):
                fn = fitness_function(finals[i], parent.depth + 5)
                gn = (len(finals) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(finals[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)

        elif len(curr_node.bracket) == 4:
            final_four_bracket = []
            final_four_bracket.extend(curr_node.east)
            final_four_bracket.extend(curr_node.west)
            final_four_bracket.extend(curr_node.south)
            final_four_bracket.extend(curr_node.midwest)
            ff_brackets = gen_states(final_four_bracket)

            for i in range(0, len(ff_brackets)):
                fn = fitness_function(ff_brackets[i], parent.depth + 5)
                gn = (len(ff_brackets) / 2) + parent.gn
                hn = fn + gn
                new_node = Node(ff_brackets[i], hn, fn, gn, parent, [], [], [], [], parent.depth + 1)
                frontier.append(new_node)
        else:
            south_brackets = gen_states(curr_node.south)
            east_brackets = gen_states(curr_node.east)
            west_brackets = gen_states(curr_node.west)
            mid_west_brackets = gen_states(curr_node.midwest)

            frontier = update_frontier(frontier, parent, south_brackets, east_brackets, west_brackets, mid_west_brackets, parent.depth + 5)
            frontier.sort(key=lambda x: x[2])

        curr_node = frontier.pop()
    print('Num Steps:', steps)
    return curr_node


def display_bracket(bracket):
    for i in range(0, len(bracket)):
        print('Game', i + 1)
        print(bracket[i][0].name, 'vs', bracket[i][1].name)


def display_rounds(root, championship):
    curr_node = championship
    curr_round = 5

    if championship.bracket[0][0].bpi > championship.bracket[0][1].bpi:
        print("Champion:", championship.bracket[0][0].name)
        winner = championship.bracket[0][0].name
    else:
        print("Champion:", championship.bracket[0][1].name)
        winner = championship.bracket[0][1].name

    while curr_node.parent is not None:
        curr_round -= 1
        print('Round', curr_round)
        if len(curr_node.bracket) < 4:
            display_bracket(curr_node.bracket)
        else:
            print("South Bracket:")
            display_bracket(curr_node.south)
            print("East Bracket:")
            display_bracket(curr_node.east)
            print("West Bracket:")
            display_bracket(curr_node.west)
            print("Midwest Bracket:")
            display_bracket(curr_node.midwest)
        print('********')
        curr_node = curr_node.parent

    print('Round', 1)
    print("South Bracket:")
    display_bracket(root.south)
    print("East Bracket:")
    display_bracket(root.east)
    print("West Bracket:")
    display_bracket(root.west)
    print("Midwest Bracket:")
    display_bracket(root.midwest)

    return winner


def get_all_teams(filename):
    rows = []
    all_teams = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            rows.append(row)

        print("Num Rows: %d"%(csvreader.line_num))

        for row in rows:
            name = row[0]
            region = row[1]
            seed = row[2]
            bpi = row[3]
            adjEM = row[4]
            prob_rd_1 = row[5]
            prob_rd_2 = row[6]
            prob_rd_3 = row[7]
            prob_rd_4 = row[8]
            prob_rd_5 = row[9]
            prob_rd_6 = row[10]
            team = Team(name, region, seed, bpi, adjEM, prob_rd_1, prob_rd_2, prob_rd_3, prob_rd_4, prob_rd_5, prob_rd_6)
            all_teams.append(team)
    return all_teams

filename = 'March_Madness_2018_19 - Sheet1.csv'
all_teams = get_all_teams(filename)
south_teams, east_teams, west_teams, mid_west_teams, = fill_team_regions(all_teams)

south_bracket = fill_region_bracket(south_teams)
east_bracket = fill_region_bracket(east_teams)
west_bracket = fill_region_bracket(west_teams)
mid_west_bracket = fill_region_bracket(mid_west_teams)

root = generate_root(south_bracket, east_bracket, west_bracket, mid_west_bracket)


championship = a_star_bpi(root)
print('~~~~~ A* BPI Solution ~~~~~')
winner = display_rounds(root, championship)
print('####################################')
championship = a_star_538(root)
print('~~~~~ A* 538 Solution ~~~~~')
winner = display_rounds(root, championship)
print('####################################')
championship = a_star_adjEM(root)
print('~~~~~ A* Adjusted EM Solution ~~~~~')
winner = display_rounds(root, championship)
print('####################################')
championship = greedy_bpi(root)
print('~~~~~ Greedy BPI Solution ~~~~~')
winner = display_rounds(root, championship)
print('####################################')
championship = greedy_538(root)
winner = display_rounds(root, championship)
print('~~~~~ Greedy 538 Solution ~~~~~')
championship = greedy_538(championship)
print('####################################')
championship = greedy_adjEM(root)
print('~~~~~ Greedy Adjusted EM Solution ~~~~~')
winner = display_rounds(root, championship)
