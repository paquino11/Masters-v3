ON DOCKER:
docker build -t ditto-ipfs-image .
docker run --name ditto-ipfs --network docker_default ditto-ipfs-image
docker ps
docker exec -it <containerID> bash


LOCALLY
change .env MONGO_DB_CLIENT=localhost:27017


sudo apt-get install python3.11 python3-pip python3.11-dev python3.11-venv

python3.11 -m venv env

source env/bin/activate

pip3 install -r requirements.txt

python app.py






