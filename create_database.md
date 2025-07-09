# Login as PostgreSQL superuser
```
sudo -u postgres psql
```
# Data
```
database_name =auction_db
database_user =auction_user
databse_password = auction_password
```
# create Database
```
CREATE DATABSE auction_db;
CREATE USER auction_user WITH PASSWORD 'auction_password';

```
# Grant ALL Permission
```
GRANT ALL PRIVILEGES ON DATABASE auction_db TO auction_user;
```