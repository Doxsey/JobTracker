To migrate the db:

flask db migrate -m "Change note here"
flask db upgrade

run on windows in dev mode python run.py

docker info:
docker build -t job-tracker .
docker save job-tracker -o job-tracker-docker.tar
