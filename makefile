BASE="volunteer_organisation"

all:
	for app in "member" "volunteer" "event"; do        \
		python $(BASE)/manage.py makemigrations $$app; \
	done
	python $(BASE)/manage.py migrate
	python ./data/create_db.py

.PHONY: clean

clean:
	for app in "member" "volunteer" "event"; do \
			rm -rf "$(BASE)/$$app/migrations";  \
	done
	rm -f $(BASE)/db.sqlite3
