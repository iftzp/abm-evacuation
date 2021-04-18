import pycxsimulator
from pylab import *

# default parameters
population_size = 20

building_width = 10
building_height = 10
number_of_storeys = 5
number_of_stairwells = 4
number_of_exits = 4
distance_to_safezone = 10

# we get the width of the building, the distance to safezone on both sides and the size of the safezone (10) on both sides and use this as total width
total_width = building_width + (distance_to_safezone * 2) + (10 * 2)
total_height = building_height + (distance_to_safezone * 2) + (10 * 2)

building_zone_label = 2
building_wall_label = 5
exit_label = 4
stairwell_label = 3
evacuation_zone_label = 0
safe_zone_label = 1

wall_padding_size = 0.4
stairwell_ratio_size = 0.3

class Agent:
    pass

def initialize():
    global time, layout, agents, building_row_values, building_column_values, floor_output, safe_output

    layout = zeros([total_height, total_width])
    layout += evacuation_zone_label

    building_row_range = (round((layout.shape[0] / 2) - (building_height / 2)), round((layout.shape[0] / 2) - (building_height / 2)) + building_height)
    building_column_range = (round((layout.shape[1] / 2) - (building_width / 2)), round((layout.shape[1] / 2) - (building_width / 2)) + building_width)

    building_row_values = [i for i in range(building_row_range[0], building_row_range[1])]
    building_column_values = [i for i in range(building_column_range[0], building_column_range[1])]

    inverse_safezone_row_values = [i for i in range(building_row_range[0] - distance_to_safezone, building_row_range[1] + distance_to_safezone)]
    inverse_safezone_column_values = [i for i in range(building_column_range[0] - distance_to_safezone, building_column_range[1] + distance_to_safezone)]

    # outline safezone by assigning values to environment matrix
    for row in range(total_height):
        for column in range(total_width):
            if row not in inverse_safezone_row_values or column not in inverse_safezone_column_values:
                layout[row, column] = safe_zone_label

    # outline building
    for row in building_row_values:
        for column in building_column_values:
            layout[row, column] = building_zone_label

    # outline walls of building
    for row in building_row_values:
        layout[row, min(building_column_values) - 1] = building_wall_label
        layout[row, max(building_column_values) + 1] = building_wall_label

    for column in building_column_values:
        layout[min(building_row_values)-1, column] = building_wall_label
        layout[max(building_row_values)+1, column] = building_wall_label

    layout[min(building_row_values)-1, min(building_column_values)-1] = building_wall_label
    layout[min(building_row_values)-1, max(building_column_values)+1] = building_wall_label
    layout[max(building_row_values)+1, min(building_column_values)-1] = building_wall_label
    layout[max(building_row_values)+1, max(building_column_values)+1] = building_wall_label

    # mark in exits
    exits = {
                0: [building_row_values, max(building_column_values)+1],
                1: [building_row_values, min(building_column_values)-1],
                2: [max(building_row_values)+1, building_column_values],
                3: [min(building_row_values)-1, building_column_values]
    }

    for exit in [i for i in range(number_of_exits)]:
        row_value_range = exits[exit][0]
        column_value_range = exits[exit][1]
        if isinstance(column_value_range, int):
            wall_size = (max(building_row_values) - min(building_row_values)) + 2
            # wall_padding = round(wall_size * wall_padding_size)
            wall_padding = int(wall_size * wall_padding_size)
            door_start = min(building_row_values) + wall_padding
            door_end = max(building_row_values) - wall_padding
            for row in range(door_start, door_end):
                layout[row, column_value_range] = exit_label
        if isinstance(row_value_range, int):
            wall_size = (max(building_column_values) - min(building_column_values)) + 2
            # wall_padding = round(wall_size * wall_padding_size)
            wall_padding = int(wall_size * wall_padding_size)
            door_start = min(building_column_values) + wall_padding
            door_end = max(building_column_values) - wall_padding
            for column in range(door_start, door_end):
                layout[row_value_range, column] = exit_label


    row_padding = int(len(building_row_values) * stairwell_ratio_size)
    column_padding = int(len(building_column_values) * stairwell_ratio_size)
    # row_padding = round(len(building_row_values) * stairwell_ratio_size)
    # column_padding = round(len(building_column_values) * stairwell_ratio_size)

    stairwells = {
        0: {'start': [min(building_row_values), min(building_column_values)], 'end': [min(building_row_values)+row_padding, min(building_column_values)+column_padding]},
        1: {'start': [max(building_row_values)-row_padding+1, max(building_column_values)-column_padding+1], 'end': [max(building_row_values)+1, max(building_column_values)+1]},
        2: {'start': [max(building_row_values)-row_padding+1, min(building_column_values)], 'end': [max(building_row_values)+1, min(building_column_values)+column_padding]},
        3: {'start': [min(building_row_values), max(building_column_values)-column_padding+1], 'end': [min(building_row_values)+row_padding, max(building_column_values)+1]}
    }

    for stairwell in [i for i in range(number_of_stairwells)]:
        start_row = stairwells[stairwell]['start'][0]
        start_column = stairwells[stairwell]['start'][1]
        end_row = stairwells[stairwell]['end'][0]
        end_column = stairwells[stairwell]['end'][1]
        for row_value in range(start_row, end_row):
            for column_value in range(start_column, end_column):
                layout[row_value, column_value] = stairwell_label

    agents = []
    safe_output = [0]
    floor_output = {}
    for i in range(population_size):
        floors = {}
        new_agent = Agent()
        agent_row = choice(building_row_values)
        agent_column = choice(building_column_values)
        while layout[agent_row, agent_column] == stairwell_label:
            agent_row = choice(building_row_values)
            agent_column = choice(building_column_values)
        new_agent.row = agent_row
        new_agent.column = agent_column
        new_agent.floor = choice(range(number_of_storeys))
        if new_agent.floor not in floor_output:
            floor_output[new_agent.floor] = []
            floor_output[new_agent.floor].append(1)
        else:
            floor_output[new_agent.floor][-1] += 1
        new_agent.status = 'unsafe'
        agents.append(new_agent)

def observe():
    global layout, agents, floor_output, safe_output
    subplot(2, 2, 1)
    cla()
    imshow(layout, cmap = cm.Paired, interpolation='none')
    agent_rows = [agent.row for agent in agents]
    agent_columns = [agent.column for agent in agents]
    agent_floors = [agent.floor for agent in agents]
    scatter(agent_columns, agent_rows, cmap = cm.bone, s=5)

    subplot(2, 2, 2)
    cla()
    x = [i for i in range(len(safe_output))]
    plot(x, safe_output)
    title('Number of safe individuals @ t = ' + str(x[-1]))

    subplot(2, 1, 2)
    cla()
    x = [i for i in range(len(floor_output[0]))]
    for key in floor_output:
        plot(x, floor_output[key], label=f'Floor {key}')
    legend()
    title('Individuals on each floor of building @ t = ' + str(x[-1]))
    plt.savefig('display.png')

def clip(a, amin, amax):
    if a < amin: return amin
    elif a > amax: return amax
    else: return a

def update():
    global layout, agents, floor_output, safe_output

    # update variables for output
    safe = 0
    for key in floor_output:
        floor_output[key].append(0)
    for agent in agents:
        if agent.floor not in floor_output:
            floor_output[agent.floor] = []
            floor_output[agent.floor].append(1)
        else:
            floor_output[agent.floor][-1] += 1
        if agent.floor == 0 and agent.status == 'safe':
            floor_output[agent.floor][-1] -= 1
        if agent.status == 'safe':
            safe += 1
    safe_output.append(safe)

    for agent in agents:
        if layout[agent.row, agent.column] == evacuation_zone_label:
            assert agent.floor == 0
            distance_to_top_or_bottom = layout.shape[0] - agent.row if agent.row > layout.shape[0] / 2 else agent.row
            distance_to_left_or_right = layout.shape[1] - agent.column if agent.column > layout.shape[1] / 2 else agent.column
            if distance_to_top_or_bottom < distance_to_left_or_right:
                if agent.row > layout.shape[0] / 2:
                    agent.row += 1
                else:
                    agent.row -= 1
                continue
            else:
                if agent.column > layout.shape[1] / 2:
                    agent.column += 1
                else:
                    agent.column -= 1
                continue

        if layout[agent.row, agent.column] == exit_label:
            assert agent.floor == 0
            new_row = agent.row + randint(-1, 2)
            new_column = agent.column + randint(-1, 2)
            while layout[new_row, new_column] != evacuation_zone_label:
                new_row = agent.row + randint(-1, 2)
                new_column = agent.column + randint(-1, 2)
            agent.row = new_row
            agent.column = new_column
            continue

        if layout[agent.row, agent.column] == building_zone_label:
            if agent.floor == 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if layout[agent.row + dx, agent.column + dy] == exit_label:
                            agent.row += dx
                            agent.column += dy
                            continue
            if agent.floor > 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if layout[agent.row + dx, agent.column + dy] == stairwell_label:
                            agent.row += dx
                            agent.column += dy
                            continue

            new_row = agent.row + randint(-1, 2)
            new_column = agent.column + randint(-1, 2)
            if agent.floor == 0:
                while layout[new_row, new_column] == building_wall_label:
                    new_row = agent.row + randint(-1, 2)
                    new_column = agent.column + randint(-1, 2)
            if agent.floor > 0:
                while layout[new_row, new_column] == building_wall_label or layout[new_row, new_column] == exit_label:
                    new_row = agent.row + randint(-1, 2)
                    new_column = agent.column + randint(-1, 2)
            agent.row = new_row
            agent.column = new_column
            continue

        if layout[agent.row, agent.column] == safe_zone_label:
            # add clip here
            if agent.status == 'unsafe':
                agent.status = 'safe'
            assert agent.floor == 0
            new_row = agent.row + randint(-1, 2)
            new_column = agent.column + randint(-1, 2)
            try:
                while layout[new_row, new_column] != safe_zone_label:
                    new_row = agent.row + randint(-1, 2)
                    new_column = agent.column + randint(-1, 2)
                agent.row = new_row
                agent.column = new_column
                agent.row = clip(agent.row, 0, layout.shape[0] - 1)
                agent.column = clip(agent.column, 0, layout.shape[1] - 1)
                continue
            except IndexError:
                agent.row = agent.row
                agent.column = agent.column
                continue

        if layout[agent.row, agent.column] == stairwell_label:
            if agent.floor == 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if layout[agent.row + dx, agent.column + dy] == exit_label:
                            agent.row += dx
                            agent.column += dy
                            continue
                new_row = agent.row + randint(-1, 2)
                new_column = agent.column + randint(-1, 2)
                while layout[new_row, new_column] == building_wall_label:
                    new_row = agent.row + randint(-1, 2)
                    new_column = agent.column + randint(-1, 2)
                agent.row = new_row
                agent.column = new_column
                continue
            if agent.floor > 0:
                agent_row = choice(building_row_values)
                agent_column = choice(building_column_values)
                while layout[agent_row, agent_column] == stairwell_label:
                    agent_row = choice(building_row_values)
                    agent_column = choice(building_column_values)
                agent.row = agent_row
                agent.column = agent_column
                agent.floor -= 1
                continue



def set_population_size(val = population_size):
    '''
    Number of individuals initially within the building.
    '''
    global population_size
    population_size = int(val)
    return val

def set_building_width(val = building_width):
    '''
    Width of building. For best performance keep below 25.
    '''
    global building_width
    building_width = int(val)
    return val

def set_building_height(val = building_height):
    '''
    Height of building. For best performance keep below 25.
    '''
    global building_height
    building_height = int(val)
    return val

def set_building_storeys(val = number_of_storeys):
    '''
    Number of storeys in building.
    '''
    global number_of_storeys
    number_of_storeys = int(val)
    return val

def set_building_stairwells(val = number_of_stairwells):
    '''
    Number of stairwells in building, between 1 and 4.
    '''
    global number_of_stairwells
    number_of_stairwells = int(val)
    return val

def set_building_exits(val = number_of_exits):
    '''
    Number of exits in building, between 1 and 4.
    '''
    global number_of_exits
    number_of_exits = int(val)
    return val

def set_distance_to_safezone(val = distance_to_safezone):
    '''
    Distance between safezone and building. For best performance keep below 10.
    '''
    global distance_to_safezone
    distance_to_safezone = int(val)
    return val

def set_wall_padding(val = wall_padding_size):
    '''
    Padding around door. Smaller value is a bigger doorway. Best not to adjust.
    '''
    global wall_padding_size
    wall_padding_size = int(val)
    return val

def set_stairwell_ratio(val = stairwell_ratio_size):
    '''
    Ratio of stairwell to rest of building. Bigger value is a bigger stairwell. Best not to adjust.
    '''
    global stairwell_ratio_size
    stairwell_ratio_size = int(val)
    return val

pycxsimulator.GUI(parameterSetters=[set_population_size, set_building_width, set_building_height, set_building_storeys, set_building_stairwells, set_building_exits, set_distance_to_safezone]).start(func=[initialize, observe, update])
