# inbuilt libraries
from datetime import datetime, timedelta
from pytz import UTC

# installed libraries
from gurobipy import *
from icalendar import Calendar, Event
import pandas as pd

# TODO: You can import functions (other than solve(...)) from a separate file if you want to organize it that way

def prepare_input(full_instance_path):
    """Loads the necessary data from a given path and converts it into usable data formats.

    Args:
        full_instance_path (string): Path to the excel file to read in

    Returns:
        (dict): Various data dictionaries
    """
    # please leave the read in mechanism like this for compatibility with tutOR
    instance_file = open(full_instance_path, 'r', encoding="utf8", errors='ignore')

    info_df = pd.read_excel(
        instance_file.buffer,
        index_col=0,
        sheet_name="info",
        engine='openpyxl'
    )

    exercise_df = pd.read_excel(
        instance_file.buffer,
        index_col=0,
        sheet_name="exercises",
        engine='openpyxl'
    )
    # TODO: Write input preparation

    return info, exercise_dict, ... # TODO: Give back what you need


def solve(full_instance_path, calendar_path):
    """Solving function, takes an instance file, builds and solves a gurobi model and returns solution.

    Args:
        full_instance_path (string): Path to the excel file to read in
        calendar_path (string): Path to the calendar file to read in

    Returns:
         model (gurobipy.model): Solved model instance
    """

    # get data from excel file
    info, exercise_dict, ... = prepare_input(full_instance_path=full_instance_path)  # TODO: Get what you need here

    # TODO: We recommend that you do define days this way, you can change it as long as the variables are named
    #  correctly later!
    # define set of weeks and days as ranges from info
    days = range(1, info["w_length"] * info["num_weeks"] + 1)

    # TODO: Write and call functions here that gets all the relevant information from the calendar file

    # create gurobipy model
    model = Model("trainmORe")

    # Variable Definition
    # TODO: Define your variables here

    # Constraints
    # TODO: Define your constraints here

    # Objective (maximize sum of priorities)
    # TODO: Define your objective here

    # update model and solve it
    model.update()
    # model.write("model.lp")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        # save a calendar with optimal workout schedule
        # TODO: You can use and adapt the output function however you like to make it work with your data formats.
        #  We recommend trying it out as the final schedule can give you a nice visual idea whether your solution is
        #  right or not.
        output(
            x=x,
            possible_times=calendar_times,
            exercise_times={e: exercise_dict[e]['duration'] for e in exercise_dict.keys()},
            info=info
        )
    else:
        print("Instance is infeasible.")

    return model


def output(x, possible_times, exercise_times, info):
    """Converts MIP solution to importable calendar file. Requires possible workout times for each day as well as
    exercise times and information on the first day of the optimized time frame and break and preparation times.

    Args:
        x (dict): Dictionary with solutions to the x variables of the solved instance
        possible_times (dict): Maximum available times and corresponding time frames for each day (keys)
        exercise_times (dict): Time required for performing each exercise (keys)
        info (dict): Used for information on break time, preparation time as well as first day of optimized time frame
    """

    # create a calendar instance
    cal = Calendar()
    cal.add("prodid", "-//workout calendar//")
    cal.add("version", "2.0")

    def create_event(start, end, name, description):
        """Takes information on times and description of an event and creates it.

        Args:
            start (datetime): Date and time of start of the event
            end (datetime): Date and time of end of the event
            name (string): Name of the event
            description (string): Description of the event
        """
        event = Event()
        event.add("summary", name)
        event.add("description", description)
        event.add("dtstart", start)
        event.add("dtend", end)
        cal.add_component(event)
        pass

    def get_workout_times(workout_time, day):
        """Calculates the start and end time of the workout.

        Args:
            workout_time (int): Workout time in minutes
            day (datetime): Day in optimization time frame

        Returns:
             start_time (datetime): Date and time of start of the workout
             end_time (datetime): Date and time of end of the workout
        """
        start_time = possible_times[day]["time_slot"][0]
        end_time = start_time + timedelta(minutes=workout_time)
        return start_time, end_time

    def get_workout_description(workouts):
        """Creates a description used for events.

        Args:
            workouts (list): List of performed exercises in a workout

        Returns:
             workouts_str (string): String used for description of calendar event
        """
        workouts_str = ""
        for i, ex in enumerate(workouts):
            workouts_str = workouts_str + ex
            if i != len(workouts) - 1:
                workouts_str = workouts_str + "\n"
        return workouts_str

    # initialization
    workout_list = []
    cur_day = 1
    cur_workout_time = 0
    for e, d in x.keys():
        # in case a day was iterated through and there was a workout, create a corresponding event
        if e == list(x.keys())[0][0] and len(workout_list) > 0:
            cur_workout_time = cur_workout_time + 2 * info['t_prep'] - info['t_break']
            start, end = get_workout_times(workout_time=cur_workout_time,
                                           day=info['first_day'] + timedelta(days=cur_day - 1))
            create_event(
                start=start,
                end=end,
                name='Workout',
                description=get_workout_description(workouts=workout_list)
            )
            workout_list = []
            cur_workout_time = 0

        # add workouts to the list for the current day
        if abs(x[e, d].x - 1) < 0.001:
            workout_list.append(e)
            cur_workout_time = cur_workout_time + exercise_times[e] + info['t_break']
            cur_day = d

        # in case there is a workout on the last day, create a corresponding event
        if e == list(x.keys())[-1][0] and d == list(x.keys())[-1][1] and len(workout_list) > 0:
            cur_workout_time = cur_workout_time + 2 * info['t_prep'] - info['t_break']
            start, end = get_workout_times(workout_time=cur_workout_time,
                                           day=info['first_day'] + timedelta(days=cur_day - 1))
            create_event(
                start=start,
                end=end,
                name='Workout',
                description=get_workout_description(workouts=workout_list)
            )

    # save calendar file to path
    f = open("workouts.ics", "wb")
    f.write(cal.to_ical())
    f.close()
    pass


if __name__ == "__main__":
    model_solved = solve(
        full_instance_path="ex1.xlsx", calendar_path="cal1.ics"
    )
