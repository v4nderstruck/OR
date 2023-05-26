from datetime import datetime, timedelta
from pytz import UTC

# installed libraries
from gurobipy import *
#from icalendar import Calendar, Event
import pandas as pd

def nanRemover(number):
    if type(number) != int:
        return -1
    else:
        return number

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

    info = []
    allExercise = []

    info = info_df.values.tolist()
    weekLen = info[0][0]
    weekNum = info[1][0]
    prep    = info[2][0]
    minWork = info[3][0]
    maxWork = info[4][0]
    pause   = info[5][0]
    minWeek = info[6][0]
    maxWeek = info[7][0]
    early   = info[8][0]
    latest  = info[9][0]
    date    = info[10][0]
    startDay = date.day
    startMonth = date.month
    startYear = date.year
    a = info[11][0][5]
    if info[11][0][4] == "+":
        if len(info[11][0]) == 7:
            a = a + info[11][0][6]
            zone = int(a)
        else:
            zone = int(a)
    else:
        if len(info[11][0]) == 7:
            a = a + info[11][0][6]
            zone = -1 * int(a)
        else:
            zone = -1 * int(a)

    exerciseList = exercise_df.values.tolist()
    names = exercise_df.axes[0]
    for i in range(1, len(exerciseList)-1):
        exercise = {}
        exercise["name"] = names[i]
        exercise["category"] = exerciseList[i][0]
        #exercise["sets"] = exerciseList[i][1]     Dont see the use for these 3
        #exercise["setMin"] = exerciseList[i][2]
        #exercise["setBreak"] = exerciseList[i][3]
        exercise["setTime"] = exerciseList[i][4]
        exercise["priority"] = exerciseList[i][5]
        exercise["biceps"] = nanRemover(exerciseList[i][7])
        exercise["chest"] = nanRemover(exerciseList[i][8])
        exercise["triceps"] = nanRemover(exerciseList[i][9])
        exercise["shoulder"] = nanRemover(exerciseList[i][10])
        exercise["abdominal"] = nanRemover(exerciseList[i][11])
        exercise["backUp"] = nanRemover(exerciseList[i][12])
        exercise["backLow"] = nanRemover(exerciseList[i][13])
        exercise["thighUp"] = nanRemover(exerciseList[i][14])
        exercise["thighLow"] = nanRemover(exerciseList[i][15])
        exercise["calves"] = nanRemover(exerciseList[i][16])
        exercise["glutes"] = nanRemover(exerciseList[i][17])
        allExercise.append(exercise)
    
    needs = {}
    lastRow = exerciseList[len(exerciseList)-1]
    needs["biceps"] = nanRemover(lastRow[7])
    needs["chest"] = nanRemover(lastRow[8])
    needs["triceps"] = nanRemover(lastRow[9])
    needs["shoulder"] = nanRemover(lastRow[10])
    needs["abdominal"] = nanRemover(lastRow[11])
    needs["backUp"] = nanRemover(lastRow[12])
    needs["backLow"] = nanRemover(lastRow[13])
    needs["thighUp"] = nanRemover(lastRow[14])
    needs["thighLow"] = nanRemover(lastRow[15])
    needs["calves"] = nanRemover(lastRow[16])
    needs["glutes"] = nanRemover(lastRow[17])

    return weekLen, weekNum, prep, minWork, maxWork, pause, minWeek, maxWeek, early, latest, startDay, startMonth, startYear, zone, allExercise, needs

weekLen, weekNum, prep, minWork, maxWork, pause, minWeek, maxWeek, early, latest, startDay, startMonth, startYear, zone, allExercise, needs = prepare_input("ex1.xlsx")