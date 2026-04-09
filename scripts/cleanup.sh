docker compose down
docker compose down --remove-orphans
docker compose down --volumes
docker compose down -v
docker volume rm beer-near-here_postgres_data
docker compose down --rmi all
docker compose stop
docker system prune -f
docker container prune -f
docker network prune -f
docker image prune -a -f
docker system prune -a --volumes -f
docker builder prune -f