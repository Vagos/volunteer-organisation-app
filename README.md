## TODO

## Evangelos
- [ ] Volunteer: Choose team page
- [ ] Volunteer: See tasks page
- [ ] Member: Sign in page
- [o] Fill Database with test data
- [ ] Fix way someone sees their Profile

## Ioanna
- [X] Volunteer, Member, Event: Create models from schema
- [X] Move Employee and Management in Volunteer app
- [X] Fix Model's on-delete behaviour
- [X] Incomes, Expenses Models
- [ ] Fix Composite Foreign keys with raw SQL

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

Views: 

```sql
CREATE VIEW team_members(volunteer_id, name, surname, team_name)
AS 
SELECT M.id, M.name, M.surname, VP.team_name_id
FROM volunteer_participation as VP, member_member as M
WHERE VP.volunteer_id_id = M.id
```

[###](###) Latex:

* https://texample.net/tikz/examples/entity-relationship-diagram/
* https://texample.net/tikz/examples/er-diagram/
* https://tex.stackexchange.com/questions/172315/draw-a-erd-in-crows-foot
* https://tex.stackexchange.com/questions/462914/how-to-create-an-er-diagram-using-tikzpicture-environment
