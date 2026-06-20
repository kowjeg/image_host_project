mkdir -p backups
docker exec -t image_server_db pg_dump -U postgres images_db \
  > "backups/backup_$(date +%F_%H%M%S).sql"