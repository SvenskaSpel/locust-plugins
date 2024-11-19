#!/bin/bash 

curl -u "$GRAFANA_CRED" $GRAFANA_HOST/api/datasources -XPOST \
-H "Accept: application/json" \
-H "Content-Type: application/json" \
-d @- << EOF
{
    "access": "proxy",
    "basicAuth": false,
    "basicAuthPassword": "",
    "basicAuthUser": "",
    "database": "postgres",
    "isDefault": false,
    "jsonData": {
        "postgresVersion": 1200,
        "sslmode": "disable",
        "timescaledb": true
    },
    "name": "$DS_NAME",
    "orgId": 1,
    "readOnly": false,
    "secureJsonData": {
        "password": "$PGPASSWORD"
    },
    "type": "postgres",
    "url": "$PGHOST:$PGPORT",
    "user": "postgres",
    "version": 3,
    "withCredentials": false
}
EOF
