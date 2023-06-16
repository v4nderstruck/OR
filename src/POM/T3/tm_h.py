# inbuilt libraries
from datetime import datetime, timedelta
from pytz import UTC

# installed libraries
from gurobipy import *
from icalendar import Calendar, Event
import pandas as pd
import icalendar
import datetime


def solve(full_instance_path, calendar_path):
    """Solving function, takes an instance file, builds and solves a gurobi model and returns solution.

    Args:
        full_instance_path (string): Path to the excel file to read in
        calendar_path (string): Path to the calendar file to read in

    Returns:
         model (gurobipy.model): Solved model instance
    """

    body_parts_names = ["Biceps", "Chest", "Shoulder", "Triceps", "Abdominals",
                        "Upper Back", "Lower Back", "Upper Thighs", "Lower Thighs", "Calves", "Glutes"]

    class ExPlan:

        def parse_body_part(self, frame, attr):
            if isinstance(frame[attr], int):
                self.body_rest[attr] = frame[attr]
            else:
                # if not any meaningfull data type, we just say it is -1
                self.body_rest[attr] = -1

        def __init__(self, df: pd.DataFrame):
            self.body_rest = {}
            self.parse_body_part(df, "Biceps")
            self.parse_body_part(df, "Chest")
            self.parse_body_part(df, "Shoulder")
            self.parse_body_part(df, "Triceps")
            self.parse_body_part(df, "Abdominals")
            self.parse_body_part(df, "Upper Back")
            self.parse_body_part(df, "Lower Back")
            self.parse_body_part(df, "Upper Thighs")
            self.parse_body_part(df, "Lower Thighs")
            self.parse_body_part(df, "Calves")
            self.parse_body_part(df, "Glutes")
            self.name = df["Name"]
            self.category = str(df["Category"]).lower()
            # Todo: sanity check against other time values
            self.totalTime = df["Total time"]
            if pd.isnull(df["Priority"]):
                self.priority = 0
            else:
                self.priority = df["Priority"]


        # overload adding for calculation of max rest
        def add(self, other):
            dominant_exercise = ExPlan(f"{self.name}&{other.name}")
            for body_part in body_parts_names:
                dominant_exercise.body_rest[body_part] = max(
                    self.body_rest[body_part], other.body_rest[body_part])

    class NeedsPlan:
        # minimum body training time needed for each muscle group

        def parse_value(self, frame, attr):
            if isinstance(frame[attr], int):
                if frame[attr] < 0:
                    frame[attr] = frame[attr] * -1
                self.body_need[attr] = frame[attr]
            else:
                # if not any meaningfull data type, we just say it is 0
                self.body_need[attr] = 0

        # a single row!
        def __init__(self, exercise_dataset: pd.DataFrame):
            self.body_need = {}
            self.parse_value(exercise_dataset, "Biceps")
            self.parse_value(exercise_dataset, "Chest")
            self.parse_value(exercise_dataset, "Shoulder")
            self.parse_value(exercise_dataset, "Triceps")
            self.parse_value(exercise_dataset, "Abdominals")
            self.parse_value(exercise_dataset, "Upper Back")
            self.parse_value(exercise_dataset, "Lower Back")
            self.parse_value(exercise_dataset, "Upper Thighs")
            self.parse_value(exercise_dataset, "Lower Thighs")
            self.parse_value(exercise_dataset, "Calves")
            self.parse_value(exercise_dataset, "Glutes")


    class ExInfo:  # describes the full exercise plan

        def __init__(self, ex_path):
            info_dataset = pd.read_excel(ex_path, sheet_name="info",  engine='openpyxl',)
            self.sanity_check_info(info_dataset)
            exercise_dataset = pd.read_excel(ex_path, sheet_name="exercises",  engine='openpyxl',)

            # load first row as column names
            exercise_dataset.columns = exercise_dataset.iloc[0]
            exercise_dataset = exercise_dataset.drop(
                exercise_dataset.index[0])  # drop first row

            self.allExercise = {}
            self.allExerciseByBody = {}
            self.needs = None
            self.sanity_check_needs(exercise_dataset)

            # drop last row
            exercise_dataset = exercise_dataset.drop(
                exercise_dataset.index[-1])
            self.sanity_check_exercise(exercise_dataset)
            self.sanity_check_exercise_by_body(exercise_dataset)

        def sanity_check_needs(self, exercise_dataset):
            last_row = exercise_dataset.iloc[-1]
            # assert last_row["Name"] == "Minimum Weekly Workout Time", "last row of exercise dataset is not minimum weekly workout time"
            self.needs = NeedsPlan(last_row)

        def sanity_check_exercise(self, exercise_dataset):
            for index, row in exercise_dataset.iterrows():
                category = row["Category"]
                # if pd.isnull(category) or pd.isnull(row["Name"]): # exercise without names or category sucks
                # assert False, f"exercise {row} has no name or category"
                self.allExercise[row["Name"]] = ExPlan(row)

        def sanity_check_exercise_by_body(self, exercise_dataset):
            for index, row in exercise_dataset.iterrows():
                category = row["Category"]
                # if pd.isnull(category) or pd.isnull(row["Name"]):
                # assert False, f"exercise {row} has no name or category"
                for i, v in row.items():
                    if i in body_parts_names and (isinstance(v, int) or isinstance(v, float)) and v >= 0:
                        if i in self.allExerciseByBody:
                            self.allExerciseByBody[i].append(row["Name"])
                        else:
                            self.allExerciseByBody[i] = [row["Name"]]

        def sanity_check_info(self, info_dataset):
            # assert info_dataset.shape == (12, 2), "info dataset has unexpected shape"
            # A table of Parameter: Value, we are guaranteed that the parameters stay the same

            # assert isinstance(info_dataset.iloc[0, 1], int), "weekLen is not an int"
            # assert info_dataset.iloc[0, 1] >= 0, f"unexpected weekLen of {info_dataset.iloc[0, 1]}"
            # assert info_dataset.iloc[0, 1] <= 7, f"unexpected weekLen of {info_dataset.iloc[0, 1]}"
            self.weekLen = info_dataset.iloc[0, 1]
            # assert isinstance(info_dataset.iloc[1, 1], int), "weekNum is not an int"
            # assert info_dataset.iloc[1, 1] >= 0, f"unexpected weekNum of {info_dataset.iloc[1, 1]}"
            self.weekNum = info_dataset.iloc[1, 1]
            # assert isinstance(info_dataset.iloc[2, 1], int), "prep is not an int"
            # assert info_dataset.iloc[2, 1] >= 0, f"unexpected prep of {info_dataset.iloc[2, 1]}"
            self.prep = info_dataset.iloc[2, 1]
            # assert isinstance(info_dataset.iloc[3, 1], int), "minWork is not an int"
            # assert info_dataset.iloc[3, 1] >= 0, f"unexpected minWork of {info_dataset.iloc[3, 1]}"
            self.minWork = info_dataset.iloc[3, 1]
            # assert isinstance(info_dataset.iloc[4, 1], int), "maxWork is not an int"
            # assert info_dataset.iloc[4, 1] >= 0, f"unexpected maxWork of {info_dataset.iloc[4, 1]}"
            # assert info_dataset.iloc[4, 1] >= self.minWork, f"maxWork {info_dataset.iloc[4, 1]} smaller than minWork {self.minWork}"
            self.maxWork = info_dataset.iloc[4, 1]
            # assert isinstance(info_dataset.iloc[5, 1], int), "pause is not an int"
            # assert info_dataset.iloc[5, 1] >= 0, f"unexpected pause of {info_dataset.iloc[5, 1]}"
            self.pause = info_dataset.iloc[5, 1]
            # assert isinstance(info_dataset.iloc[6, 1], int), "minWeek is not an int"
            # assert info_dataset.iloc[6, 1] >= 0, f"unexpected minWeek of {info_dataset.iloc[6, 1]}"
            self.minWeek = info_dataset.iloc[6, 1]
            # assert isinstance(info_dataset.iloc[7, 1], int), "maxWeek is not an int"
            # assert info_dataset.iloc[7, 1] >= 0, f"unexpected maxWeek of {info_dataset.iloc[7, 1]}"
            # assert info_dataset.iloc[7, 1] >= self.minWeek, f"maxWeek {info_dataset.iloc[7, 1]} smaller than minWeek {self.minWeek}"
            self.maxWeek = info_dataset.iloc[7, 1]
            # assert isinstance(info_dataset.iloc[8, 1], int), "early is not an int"
            # assert info_dataset.iloc[8, 1] >= 0, f"unexpected early of {info_dataset.iloc[8, 1]}"
            # assert info_dataset.iloc[8, 1] <= 24, f"unexpected early of {info_dataset.iloc[8, 1]}"
            self.early = info_dataset.iloc[8, 1]
            # assert isinstance(info_dataset.iloc[9, 1], int), "latest is not an int"
            # assert info_dataset.iloc[9, 1] >= 0, f"unexpected latest of {info_dataset.iloc[9, 1]}"
            # assert info_dataset.iloc[9, 1] <= 24, f"unexpected latest of {info_dataset.iloc[9, 1]}"
            # assert info_dataset.iloc[9, 1] >= self.early, f"latest {info_dataset.iloc[9, 1]} smaller than early {self.early}"
            self.latest = info_dataset.iloc[9, 1]
            # assert isinstance(info_dataset.iloc[10, 1], datetime.date), "startDay is not a date"
            # assert isinstance(info_dataset.iloc[11, 1], str), "zone is not a string"
            # remove spaces from zone
            zone = info_dataset.iloc[11, 1].replace(" ", "")
            # assuming UTC+X format

            zone = zone[3:]
            offset_sign = zone[0]
            offset_val = int(zone[1:])

            if offset_sign == "-":
                offset_val = -1 * offset_val

            tz = datetime.timezone(datetime.timedelta(hours=offset_val))
            self.zone = tz
            self.startDay = info_dataset.iloc[10, 1].replace(
                tzinfo=datetime.timezone.utc).astimezone(tz=self.zone)
            self.startDay = self.startDay.replace(hour=0)

    class UserEvent:

        def __init__(self, event, start, end, stamp, isExercise=False, exercises=[]):
            self.event = event
            self.start = start
            self.end = end
            self.stamp = stamp
            self.isExercise = isExercise
            self.exercises = exercises


    class DayEventIterator:
        def __init__(self, events):
            self.events = events
            self.index = 0

        def next(self):
            # returns list of events grouped by day
            if self.index < len(self.events):
                day = self.events[self.index].start.date()
                day_events = []
                while self.index < len(self.events) and self.events[self.index].start.date() == day:
                    day_events.append(self.events[self.index])
                    self.index = self.index + 1
                return day_events
            return "END_ITERATOR"

    class UserCalendar:
        def __init__(self, tz, start_date=datetime.date.today()):
            self.tz_shift = tz
            self.events = []
            self.start_date = start_date

        # note: Fixed timezones!
        def load_calendar(self, cpath):
            file = open(cpath)
            cal = icalendar.Calendar.from_ical(file.read())
            for component in cal.walk():
                if component.name == "VEVENT":
                    ds = component.decoded("dtstart")
                    dt = component.decoded("dtend")
                    dst = component.decoded("dtstamp")
                    ds = ds.replace(tzinfo=datetime.timezone.utc).astimezone(
                        tz=self.tz_shift)
                    dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone(
                        tz=self.tz_shift)
                    dst = dst.replace(tzinfo=datetime.timezone.utc).astimezone(
                        tz=self.tz_shift)
                    event = str(component.decoded(
                        "summary").decode("utf-8"))
                    event = event.lower().replace(" ", "")
                    if event.startswith("workout"):
                        desc = component.get("description")
                        desc = [x.strip()
                                for x in desc.split(',')[0].split("\n")]
                        self.events.append(UserEvent(
                            event=event,
                            start=ds,
                            end=dt,
                            stamp=dst,
                            isExercise=True,
                            exercises=desc
                        ))
                    else:
                        self.events.append(UserEvent(
                            event=event,
                            start=ds,
                            end=dt,
                            stamp=dst
                        ))
            self.events.sort(key=lambda x: x.start)
            self.day_iter = DayEventIterator(self.events)
            file.close()


    def calc_collision_pairs(info):
        blocking_exercises = {}
        for ex in info.allExercise.values():
            for body_part, rest_days in ex.body_rest.items():
                if rest_days > 0:
                    # print(f"Performing {ex.name} must Rest {body_part} for {rest_days} days blocking exercises: {info.allExerciseByBody[body_part]}")
                    for blocking_ex in info.allExerciseByBody[body_part]:
                        if ex.name in blocking_exercises:
                            if blocking_ex in blocking_exercises[ex.name]:
                                blocking_exercises[ex.name][blocking_ex] = max(
                                    rest_days, blocking_exercises[ex.name][blocking_ex])
                            else:
                                blocking_exercises[ex.name][blocking_ex] = rest_days
                        else:
                            blocking_exercises[ex.name] = {
                                blocking_ex: rest_days}
        return blocking_exercises

    def calc_day_timeslot(exercise_plan, day_events):
        # print(f"{day_events[0].stamp.date()} events {[x.event for x in day_events]}")
        # we precheck against the earliest first
        earliest_start_time = datetime.datetime.combine(
            day_events[0].start.date(),
            datetime.time(hour=exercise_plan.early, minute=0, second=0))
        earliest_start_time = earliest_start_time.replace(
            tzinfo=exercise_plan.zone)
        max_timeslot = (day_events[0].start -
                        earliest_start_time).total_seconds() / 60
        gap = ["earliest", day_events[0].event]
        for previous_event, current_event in zip(day_events, day_events[1:]):
            diff_min = (current_event.start -
                        previous_event.end).total_seconds() / 60
            if diff_min > max_timeslot:
                gap = [previous_event.event, current_event.event]
                max_timeslot = diff_min
        # we also check against the latest
        latest_end_time = datetime.datetime.combine(
            day_events[-1].start.date(),
            datetime.time(hour=exercise_plan.latest, minute=59, second=00))
        latest_end_time = latest_end_time.replace(tzinfo=exercise_plan.zone)
        diff_min = (latest_end_time - day_events[-1].end).total_seconds() / 60
        if diff_min > max_timeslot:
            max_timeslot = diff_min
            gap = [day_events[-1].event, "latest"]

        # print(f"max_timeslot of day {day_events[0].stamp.date()}: {max_timeslot}min in beween {gap[0]} and {gap[1]}")
        return max_timeslot

    def build_simple_model(info, cal):
        import gurobipy as gp
        blocking_exercises = calc_collision_pairs(info)
        model = gp.Model("workout")
        days = [i for i in range(1, info.weekLen * info.weekNum + 1)]

        # should train on day
        d = {}
        for day_c in days:
            d[day_c] = model.addVar(
                vtype=gp.GRB.BINARY, obj=0.0, name=f"d_{day_c}")

        # variables for exercise selection
        x = {}
        for day_c in days:
            for ex in info.allExercise:
                x[f"{ex}_{day_c}"] = model.addVar(
                    vtype=gp.GRB.BINARY, obj=1.0, name=f"x_{ex}_{day_c}")
        
        # training time of body part per day
        training_time = {}
        for day_c in days:
            for body_part in body_parts_names:
                training_time[f"{body_part}_{day_c}"] = model.addVar(
                    vtype=gp.GRB.CONTINUOUS, obj=0.0, name=f"t_{body_part}_{day_c}")

        # constr: only train if we have exercises selected
        for day_c in days:
            for ex in info.allExercise:
                model.addConstr(x[f"{ex}_{day_c}"] <= d[day_c],
                                name=f"only_train_if_day_{ex}_{day_c}")

        # constr: we do excactly one warmup if we train on that day
        warumups = [
            w for w in info.allExercise if info.allExercise[w].category == "warm up"]
        for day_c in days:
            model.addConstr(gp.quicksum(
                x[f"{ex}_{day_c}"] for ex in warumups) == d[day_c], name=f"only_one_warmup_{day_c}")

        # constr: if we perform an exercise, we add the exercise time to the training time of the body part
        for day_c in days:
            for body_part, exercises in info.allExerciseByBody.items():
                model.addConstr(
                    gp.quicksum(
                        x[f"{ex}_{day_c}"] * info.allExercise[ex].totalTime for ex in exercises)
                    ==
                    training_time[f"{body_part}_{day_c}"],
                    name=f"training_time_{body_part}_{day_c}"
                )

        # constr: consider the minimum and maximum training time for each workout
        for day_c in days:
            model.addConstr(
                gp.quicksum(
                    x[f"{ex}_{day_c}"] * (info.allExercise[ex].totalTime + info.pause) for ex in info.allExercise
                ) - info.pause * d[day_c]
                >= info.minWork * d[day_c],
                name=f"min_work_{day_c}")

            model.addConstr(
                gp.quicksum(
                    x[f"{ex}_{day_c}"] * (info.allExercise[ex].totalTime + info.pause) for ex in info.allExercise
                ) - info.pause * d[day_c]
                <= info.maxWork * d[day_c],
                name=f"max_work_{day_c}")

        # constr: for each week, we need to train at least minWeek and at most maxWeek
        # constr: also we have to consider per body part training times
        for week in range(0, info.weekNum):
            days_of_week = [i for i in range(
                week * info.weekLen + 1, week * info.weekLen + info.weekLen + 1)]
            model.addConstr(gp.quicksum(
                d[day] for day in days_of_week) >= info.minWeek, name=f"min_week_{week}")
            model.addConstr(gp.quicksum(
                d[day] for day in days_of_week) <= info.maxWeek, name=f"max_week_{week}")
            for body_part, time in info.needs.body_need.items():
                model.addConstr(gp.quicksum(
                    training_time[f"{body_part}_{day}"] for day in days_of_week) >= time, name=f"min_week_{week}_{body_part}")

        # general training rule

        # constr: we need to consider the calendar and find free time slots
        print(f"startDay: {info.startDay}")
        block_on_day = {}  # starting with 0 for startday
        visited_days = set()
        day_events = cal.day_iter.next()
        while day_events != "END_ITERATOR":
            this_day = day_events[0].start.date()
            diff_days = (this_day - info.startDay.date()).days
            if diff_days < 0:  # if event is before startDay, we only collect exercises
                for event in day_events:
                    if event.isExercise:  # event was an exercise
                        print(
                            f"Prior Exercise on {event.start.date()}: {event.exercises}")
                        for exercise in event.exercises:
                            if exercise in blocking_exercises:
                                for blocking_ex, rest_days in blocking_exercises[exercise].items():
                                    if rest_days + diff_days >= 0:  # block exercise if it will our plan
                                        if rest_days + diff_days in block_on_day:
                                            block_on_day[rest_days +
                                                         diff_days].add(blocking_ex)
                                        else:
                                            block_on_day[rest_days +
                                                         diff_days] = {blocking_ex}
            else:  # we are at start of exercise plan phase
                max_workout_time = calc_day_timeslot(info, day_events)
                print(
                    f"Max Workout Time on {this_day}: {max_workout_time} with {2*info.prep} prep time and {info.pause} pause time")
                if diff_days+1 > info.weekLen * info.weekNum:
                    day_events = cal.day_iter.next()
                    continue
                visited_days.add(diff_days+1)
                model.addConstr(
                    gp.quicksum(
                        x[f"{ex}_{diff_days+1}"] * 
                        (info.allExercise[ex].totalTime + info.pause) for ex in info.allExercise
                    ) - info.pause * d[diff_days + 1] + 2 * info.prep * d[diff_days+1]
                    <= max_workout_time * d[diff_days + 1],
                    name=f"max_workout_time_{diff_days+1}"

                )

            day_events = cal.day_iter.next()

        # constr: we need to consider the block on day block
        print(block_on_day)
        for day_c, blocking_exs in block_on_day.items():
            for blocking_ex in blocking_exs:
                model.addConstr(
                    x[f"{blocking_ex}_{day_c+1}"] == 0,
                    name=f"block_on_day_{blocking_ex}_{day_c+1}"
                )
        max_training_time = (info.latest - info.early) * 60
        max_training_time += 59
        for day_c in days:
            if day_c not in visited_days:
                model.addConstr(
                    gp.quicksum(
                        x[f"{ex}_{day_c}"] * (info.allExercise[ex].totalTime + info.pause) for ex in info.allExercise
                    ) - info.pause * d[day_c] + 2 * info.prep * d[day_c]
                    <= max_training_time * d[day_c],
                    name=f"max_workout_time_{day_c}"
                )
        # constr: now add days that were not visited
        for day_c in days:
            if day_c >= info.weekLen * info.weekNum:
                continue  # dont care about last day
            for ex, blocking_exs in blocking_exercises.items():
                for blocking_ex, rest_days in blocking_exs.items():
                    if rest_days <= 0:  # if rest is 0, we dont need to block
                        continue
                    ran = []
                    # if rest would go out of timespan, we just block until end
                    if day_c + 1 + rest_days > info.weekLen * info.weekNum:

                        #                ^ This was >=. If we do a workout with rest day 1 on day 19, we should be able to do it on day 21. If >= we cannot.

                        ran = [t for t in range(
                            day_c + 1, info.weekLen * info.weekNum + 1)]
                    else:  # else we block until rest days are over starting from next day
                        ran = [t for t in range(
                            day_c + 1, day_c + rest_days + 1)]
                    # print(f"Blocking {blocking_ex} for {ran} after {ex}")
                    for d in ran:
                        model.addConstr(
                            x[f"{blocking_ex}_{d}"]
                            <= (1 - x[f"{ex}_{day_c}"]),
                            name=f"block_{blocking_ex}_{d}_{ex}_{day_c}"
                        )

        model.update()
        # objective: maximize priority
        model.setObjective(gp.quicksum(
            x[f"{ex}_{day}"] * info.allExercise[ex].priority for ex in info.allExercise for day in days), gp.GRB.MAXIMIZE)
        model.write("workout.lp")
        model.update()
        model.optimize()  # todo: find mistake obj is off
        return model

    ex = ExInfo(full_instance_path)
    cal = UserCalendar(ex.zone)
    cal.load_calendar(calendar_path)
    model = build_simple_model(ex, cal)
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
            cur_workout_time = cur_workout_time + \
                2 * info['t_prep'] - info['t_break']
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
            cur_workout_time = cur_workout_time + \
                exercise_times[e] + info['t_break']
            cur_day = d

        # in case there is a workout on the last day, create a corresponding event
        if e == list(x.keys())[-1][0] and d == list(x.keys())[-1][1] and len(workout_list) > 0:
            cur_workout_time = cur_workout_time + \
                2 * info['t_prep'] - info['t_break']
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
        full_instance_path="ex2.xlsx", calendar_path="cal2.ics"
    )
