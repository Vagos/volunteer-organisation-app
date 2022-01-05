import sqlite3
import random
import string

base = "./data"

with open(base + "/member_usernames.txt", "r") as member_name_file:

    member_names, member_surnames = member_name_file.read().strip().split('\n\n')

    member_names = member_names.split('\n')
    member_surnames = member_surnames.split('\n')

with open(base + "/events.txt", "r") as events_file:

    event_categories, event_name_verbs, event_name_cause, event_places = events_file.read().strip().split('\n\n')

    event_name_verbs = event_name_verbs.split('\n')
    event_name_cause = event_name_cause.split('\n')
    event_categories = event_categories.split('\n')
    event_places = event_places.split('\n')

with open(base + "/tasks.txt", "r") as tasks_file:

    task_verbs, task_targets = tasks_file.read().strip().split('\n\n')

    task_verbs = task_verbs.split('\n')
    task_targets = task_targets.split('\n')


def create_string(l=20):
    return ''.join((random.choice(string.ascii_letters + ' ') for i in range(l)))

def create_username(names, surnames):

    name = random.choice(names)
    surname = random.choice(surnames)

    return name, surname

def create_date(previous_date = "2015-1-1"):
    """ Create a random date that happens AFTER previous_date."""

    p_y, p_m, p_d = (int(i) for i in previous_date.split('-'))

    y = random.randint(p_y, 2022)
    m = random.randint(p_m, 12)
    d = random.randint(p_d, 28 if m == 2 else 30)

    return "%d-%d-%d" % (y, m, d)

def create_event(categories, verbs, causes, places):

    event_name = random.choice(verbs) + ' ' + random.choice(causes)

    start_date = create_date()
    end_date = create_date(start_date)

    place = random.choice(places)
    description = create_string(20)
    category = random.choice(categories)

    return (event_name, start_date, end_date, place, description, category)



def create_team(targets, occupation):
    team_name = random.choice(targets) + ' ' + random.choice(occupation)
    description = "We try to " + create_string(30)

    return (team_name, description)

def create_task(verbs, targets):

    name = random.choice(verbs) + ' ' + random.choice(targets)

    entry_date = create_date()
    due_date = create_date(entry_date)

    difficulty = random.randint(1, 10)
    completed = False

    creator = cursor.execute("select member_ptr_id from volunteer_employee order by random() limit 1").fetchone()[0]
    event = cursor.execute("select id from event_event order by random() limit 1").fetchone()[0]

    return (name, due_date, entry_date, difficulty, completed, creator, event)



def create_income():
    pass

def add_members(n=10):
    
    cmd = """
    CREATE TABLE IF NOT EXISTS "member" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "fname" varchar(30) NOT NULL,
    "lname" varchar(30) NOT NULL,
    "date_of_birth" date DEFAULT NULL,
    "email" varchar(50) DEFAULT NULL,
    "city_of_residence" varchar(50) NULL,
    "phone_number" varchar(13) NULL
    );
    """
    print(cmd)

    cursor.execute(cmd)

    for i in range(n):
        username = create_username(member_names, member_surnames)
        cmd = "INSERT INTO member (fname, lname) VALUES('%s', '%s');" % username
        print(cmd)

    cursor.execute(cmd)

def add_volunteers(n=10):

    cmd = """
    CREATE TABLE IF NOT EXISTS "volunteer"
    ("id" integer NOT NULL PRIMARY KEY REFERENCES "member" ("id"),
    "join_date" date NOT NULL
    );
    """

    print(cmd)

    cursor.execute(cmd)

    def create_volunteer():

        id = cursor.execute("SELECT id FROM member ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        join_date = create_date()

        return (id, join_date)

    for i in range(n):
        volunteer = create_volunteer()
        
        cmd = """
        INSERT INTO volunteer VALUES('%s', '%s');
        """ % volunteer

        print(cmd)

        try:
            cursor.execute(cmd)
        except sqlite3.IntegrityError:
            pass

def add_event_categories():

    cmd = """
    DROP TABLE IF EXISTS event_category;

    CREATE TABLE IF NOT EXISTS "event_category"
    ("name" varchar(30) NOT NULL PRIMARY KEY);
    """

    print(cmd)

    for c in event_categories:
        cmd = """
        INSERT INTO event_eventcategory (name) values('%s');
        """ 
        print(cmd)
        # cursor.execute(cmd)

def add_events():
    for i in range(10):
        event = create_event(event_categories, event_name_verbs, event_name_cause, event_places)

        cmd = """INSERT INTO event_event (name, start_date, end_date, place, description, category_id)
               values('%s', '%s', '%s', '%s', '%s', '%s')""" % event

        print(cmd)
        cursor.execute(cmd)

def add_employees(n=10):


    cmd = """
    CREATE TABLE IF NOT EXISTS  "employee" 
    (
        "id" int NOT NULL,
        "compensation" int NOT NULL DEFAULT 0,
        "position_name" varchar(30) NOT NULL DEFAULT '',

        CONSTRAINT "employee_fk" FOREIGN KEY("id") REFERENCES "member"("id") ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT compensation_positive CHECK (compensation > 0),
        PRIMARY KEY("id")
    );
    """

    print(cmd)

    def create_employee():

        _id = cursor.execute("SELECT id FROM member ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        compensation = random.randint(100, 10_000)
        position_name = "A Position"

        return (_id, compensation, position_name)

    for i in range(n):
        employee = create_employee()
        try:

            cmd = "INSERT INTO volunteer_employee VALUES(%d, %d, '%s')" % employee

            print(cmd)

            cursor.execute(cmd)

        except sqlite3.IntegrityError:
            pass

def add_tasks(n=10):

    cmd = """
    CREATE TABLE IF NOT EXISTS "task" 
    (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(20) NOT NULL,
    "due_date" date NOT NULL, 
    "entry_date" date DEFAULT NULL,
    "difficulty" smallint NOT NULL DEFAULT '1',
    "completed" book NOT NULL,
    "creator" integer NOT NULL REFERENCES "employee"("id"),
    "event" integer NOT NULL REFERENCES "event"("id")
    );
    """

    print(cmd)

    cursor.execute(cmd)

    for i in range(n):
        task = create_task(task_verbs, task_targets)

        cmd = """INSERT INTO task (name, due_date, entry_date, difficulty, completed, creator, event)
       VALUES('%s', '%s', '%s', %d, %d, %d, %d)""" % task

        print(cmd)

        cursor.execute(cmd)

def add_workson(n=10):

    cmd = """
    CREATE TABLE IF NOT EXISTS  "works_on" 
    (
    volunteer integer NOT NULL,
    task integer NOT NULL,

    PRIMARY KEY ("volunteer", "task"),
    CONSTRAINT "works_on_fk0" FOREIGN KEY("volunteer") REFERENCES "volunteer" ("id") ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT "works_on_fk1" FOREIGN KEY("task") REFERENCES "task" ("id") ON DELETE CASCADE  ON UPDATE CASCADE
    );
"""
    print(cmd)

    cursor.execute(cmd)

    def create_workson():

        volunteer = cursor.execute("SELECT id FROM volunteer ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        task = cursor.execute("SELECT id FROM task ORDER BY RANDOM() LIMIT 1").fetchone()[0]

        evaluation = "I think the task was done " + create_string(10);

        return (evaluation, task, volunteer)

    for i in range(n):
        workson = create_workson()

        cmd = """
        INSERT INTO volunteer_workson (evaluation, task_id_id, volunteer_id_id)
        VALUES('%s', %d, %d)
        """ % workson

        print(cmd)

        cursor.execute(cmd)

def add_teamparticipations(n=10):

    cmd = """
    CREATE TABLE IF NOT EXISTS "team_participation"
    (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "start_date" date NOT NULL,
    "end_date" date NULL, 
    "team" varchar(200) NOT NULL REFERENCES "team" ("name"),
    "volunteer" integer NOT NULL REFERENCES "volunteer" ("id")
    );
    """

    print(cmd)

    cursor.execute(cmd)

    def create_teamparticipation():

        start_date = create_date()
        end_date = create_date(start_date)

        volunteer = cursor.execute("SELECT id FROM volunteer ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        team = cursor.execute("SELECT name FROM team ORDER BY RANDOM() LIMIT 1").fetchone()[0]

        return (start_date, end_date, volunteer, team)

    for i in range(n):

        team_participation = create_teamparticipation()

        cmd = """
        INSERT INTO team_participation (start_date, end_date, volunteer, team) VALUES('%s', '%s', %d, '%s')
        """ % team_participation

        print(cmd)

        cursor.execute(cmd)

def add_eventorganisations(n=10):

    def create_eventorganisation():

        reason = "Event created because " + create_string(20)
        entry_date = "DATE('now')" # This should be before the event's start date.
        event_id_id = cursor.execute("SELECT id FROM event_event ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        organiser_id_id = cursor.execute("SELECT member_ptr_id FROM volunteer_employee ORDER BY RANDOM() LIMIT 1").fetchone()[0]

        return (reason, entry_date, event_id_id, organiser_id_id)

    for i in range(n):

        eventorganisation = create_eventorganisation()

        cmd = """
        INSERT INTO volunteer_eventorganisation (reason, entry_date, event_id_id, organiser_id_id) VALUES('%s', %s, %d, %d)
        """ % eventorganisation

        try:
            print(cmd)
            cursor.execute(cmd)
        except sqlite3.IntegrityError:
            pass


def add_teams(n=10):

    with open(base + "/teams.txt", "r") as teams_file:

        team_targets, team_occupation = teams_file.read().strip().split('\n\n')

        team_targets    = team_targets.split('\n')
        team_occupation = team_occupation.split('\n')

    cmd = """
    CREATE TABLE IF NOT EXISTS team 
    (
    "name" varchar(100) NOT NULL PRIMARY KEY,
    "description" varchar(300) NOT NULL
    );
    """

    print(cmd)

    cursor.execute(cmd)

    for i in range(n):
        team = create_team(team_targets, team_occupation)

        cmd = """
        INSERT INTO team (name, description) VALUES('%s', '%s')
        """ % team

        print(cmd)

        try:
            cursor.execute(cmd)
        except sqlite3.IntegrityError:
            pass

def add_eventparticipations(n=10):

    def create_eventparticipation():

        date = create_date()
        impressions = "I thought the event was " + create_string(10)
        member = cursor.execute("SELECT id FROM member ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        event = cursor.execute("SELECT id FROM event ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        duration = 'null'

        return (date, duration, impressions, event, member)

    for i in range(n):
        event_participation = create_eventparticipation()

        cmd = """
        INSERT INTO volunteer_eventparticipation (date, duration, impressions, event_id_id, member_id_id) VALUES('%s', '%s', '%s', '%s', '%s')
        """ % event_participation

        print(cmd)

        cursor.execute(cmd)

def add_incomes(n=10):

    def create_income():
        participation = cursor.execute("SELECT id FROM volunteer_eventparticipation ORDER BY RANDOM() LIMIT 1").fetchone()[0]
        value = random.randint(1, 10000)
        date = create_date() # this should be betwen the dates of the event participation

        return (value, date)

connection = sqlite3.connect("volunteer_organisation/db.sqlite3")
cursor = connection.cursor()

def CreateViews():

    cmd = """
    CREATE VIEW team_members(volunteer_id, name, surname, team_name) AS
    SELECT M.id, M.name, M.surname, VP.team_name_id
    FROM volunteer_participation as VP, member_member as M
    WHERE VP.volunteer_id_id = M.id;
    """

    print(cmd)
    cursor.execute(cmd)

    cmd = """
    CREATE VIEW volunteer_task_assigned(volunteer_id, volunteer_name, volunteer_surname, task_id, task_name) AS
    SELECT M.id, M.name, M.surname, VT.id, VT.name
    FROM volunteer_task as VT, member_member as M, volunteer_workson as VW
    WHERE VW.task_id_id = VT.id AND VW.volunteer_id_id = M.id;
    """

    print(cmd)
    cursor.execute(cmd)

def main():

    add_members()

    add_event_categories()
    add_events()

    add_volunteers()
    add_employees()

    add_tasks()

    add_teams()
    add_workson()
    add_teamparticipations()

    add_eventorganisations()

    add_eventparticipations()

    CreateViews()
    

main()


connection.commit()
connection.close()
