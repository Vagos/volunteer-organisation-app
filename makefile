BASE="volunteer_organisation"

all:
	for app in "member" "volunteer" "event"; do \
		python $(BASE)/manage.py makemigrations $$app; \
	done
	python $(BASE)/manage.py migrate

.PHONY: clean

clean:
	for app in "member" "volunteer" "event"; do \
			rm -r "$(BASE)/$$app/migrations"; \
	done
	rm $(BASE)/db.sqlite3
