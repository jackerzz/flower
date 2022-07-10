# Broker settings
FLOWER_BROKER_URL = 'redis://:myredis@192.168.95.120:6379/2'
FLOWER_address='0.0.0.0'
FLOWER_basic_auth="admin:Pas1234"
FLOWER_db = 'logs/flowerdb'
# Enable debug logging
logging = 'DEBUG'