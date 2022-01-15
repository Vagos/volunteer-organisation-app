## Installation Instructions

### Requirments

django, matplotlib

```bash
$ git clone https://github.com/Vagos/volunteer-organisation-app
$ cd volunteer-organisation-app

$ make # create the database
$ make clean # remove the database

$ python volunteer_organisation/manage.py runserver
```

Head over to: http://127.0.0.1:8000/

## TODO

## Evangelos
- [X] Fix way someone sees their Profile
- [X] Member: Sign in page
- [X] Volunteer: Choose team page
- [X] Volunteer: See tasks page
- [X] Fill Database with test data
- [X] Find hardest working volunteer/Volunteer of the month
- [ ] Color code tasks based on difficulty

## Ioanna
- [X] In event participation, member_id and event_id should be unique.
- [X] Fix Composite Foreign keys with raw SQL
- [X] Fix Model's on-delete behaviour
- [X] Incomes, Expenses Models
- [X] Move Employee and Management in Volunteer app
- [X] Volunteer, Member, Event: Create models from schema
- [ ] Report
- [ ] Final ERD - Schema


## Resources

https://reactjs.org/tutorial/tutorial.html
https://docs.djangoproject.com/en/3.2/intro/tutorial03/

### Django:

* django-admin startproject mysite
* python manage.py startapp myapp

- Migrations:

* python manage.py makemigrations myapp

### SQLite

* https://stackoverflow.com/questions/15819186/sqlite-create-unique-pair-of-columns
* https://www.sqlitetutorial.net

Views:

```sql
CREATE VIEW team_members(volunteer_id, name, surname, team_name)
AS
SELECT M.id, M.name, M.surname, VP.team_name_id
FROM volunteer_participation as VP, member_member as M
WHERE VP.volunteer_id_id = M.id
```

Constraints:

```sql
ALTER TABLE dbo.yourtablename
  ADD CONSTRAINT uq_yourtablename UNIQUE(column1, column2);


create table foo
(
   from_date date,
   to_date date,
   constraint check_dates check (from_date < to_date)
);
```

### CSS/HTML

* https://github.com/bradtraversy/design-resources-for-developers

### Latex:

* https://texample.net/tikz/examples/entity-relationship-diagram/
* https://texample.net/tikz/examples/er-diagram/
* https://tex.stackexchange.com/questions/172315/draw-a-erd-in-crows-foot
* https://tex.stackexchange.com/questions/462914/how-to-create-an-er-diagram-using-tikzpicture-environment
