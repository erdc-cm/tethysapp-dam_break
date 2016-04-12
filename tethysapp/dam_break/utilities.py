# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os

def generate_flood_hydrograph(peak_flow, time_to_peak, peak_duration, falling_limb_duration):
    """
    Returns a flood hydrograph as a list of time value pairs.
    """
    # Magic numbers
    TIMESTEPS_PER_HOUR = 6 # for 10 minute timesteps (i.e.: 6 * 10 = 60)
    BUFFER_TIMESTEPS = 5
    INITIAL_FLOW = 0.0
    TIME_STEP = timedelta(minutes=10)
    FIRST_STAGE_FACTOR = 1.0 / 3.0
    DECIMALS = 2

    # Initial conditions
    hydrograph = []
    date = datetime(year=2010, month=6, day=7, hour=11, minute=50)

    # Initial Buffer
    for i in range(BUFFER_TIMESTEPS):
        date += TIME_STEP
        hydrograph.append([date, INITIAL_FLOW])

    # Calculate Rising Limb
    steps = int(time_to_peak * TIMESTEPS_PER_HOUR)
    rise_rate = peak_flow / steps

    for i in range(steps):
        date += TIME_STEP
        flow = INITIAL_FLOW + (rise_rate * (i + 1))
        hydrograph.append([date, round(flow, DECIMALS)])

    # Calculate Peak Duration
    steps = int(peak_duration * TIMESTEPS_PER_HOUR)

    for i in range(steps):
        date += TIME_STEP
        hydrograph.append([date, peak_flow])

    # Calculate Falling Limb
    ## First Stage
    first_stage_flow = peak_flow * FIRST_STAGE_FACTOR
    first_stage_duration = falling_limb_duration * FIRST_STAGE_FACTOR
    steps = int(first_stage_duration * TIMESTEPS_PER_HOUR)
    rate = (peak_flow - first_stage_flow) / steps

    for i in range(steps):
        date += TIME_STEP
        flow = peak_flow - (rate * (i + 1))
        hydrograph.append([date, round(flow, DECIMALS)])

    ## Second Stage
    second_stage_duration = falling_limb_duration - first_stage_duration
    steps = int(second_stage_duration * TIMESTEPS_PER_HOUR)
    rate = first_stage_flow / steps

    for i in range(steps):
        date += TIME_STEP
        flow = first_stage_flow - (rate * (i + 1))
        hydrograph.append([date, round(flow, DECIMALS)])

    # Trailing Buffer
    for i in range(BUFFER_TIMESTEPS):
        date += TIME_STEP
        hydrograph.append([date, INITIAL_FLOW])

    return hydrograph


def write_hydrograph_input_file(username, hydrograph):
    """
    Create the GSSHA input file needed to run the model.
    """
    project_directory = os.path.dirname(__file__)
    user_workspace = os.path.join(project_directory, 'workspaces', 'user_workspaces')

    if not os.path.exists(user_workspace):
        os.makedirs(user_workspace)

    input_file = os.path.join(user_workspace, 'ProvoStochastic.ihg')

    with open(input_file, 'w') as f:
        f.write('NUMPT 1\r\n')
        f.write('POINT 1 1 0.0\r\n')
        f.write('NRPDS {0}\r\n'.format(len(hydrograph)))

        for step in hydrograph:
            date = step[0]
            flow = step[1]

            # INPUT 2010 06 07 12 00 0.000000
            line = 'INPUT {0} {1:02d} {2:02d} {3:02d} {4:02d} {5}\r\n'.format(
                date.year,
                date.month,
                date.day,
                date.hour,
                date.minute,
                round(flow, 6)
            )

            f.write(line)
