import psycopg2

conn = psycopg2.connect(
    database='vital-cat-208.defaultdb',
    user='asap_verg',
    password='VnG9hSgLqu6SQx@',
    sslmode='require',
    sslrootcert='certs/ca.crt',
    sslkey='certs/client.maxroach.key',
    sslcert='certs/client.maxroach.crt',
    port=26257,
    host='free-tier.gcp-us-central1.cockroachlabs.cloud'
)
