BASE="volunteer_organisation"

all:
	python $(BASE)/manage.py migrate
	python ./data/create_db.py > db_dump.sqlite

.PHONY: clean

clean:
	rm -f $(BASE)/db.sqlite3
	rm db_dump.sqlite
