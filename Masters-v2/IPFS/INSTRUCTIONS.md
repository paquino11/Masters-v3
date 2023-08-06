docker build -t ipfs-docker .

docker run --name ipfs --network docker_default ipfs-docker
