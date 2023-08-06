
# how to use this:

logger = LogManager('logger_name').get_and_add_handlers(log_level_int=1, is_add_stream_handler=True, log_path=None, log_filename=None, log_file_size=10,mongo_url=None,formatter_template=2)

logger.debug('hello')

logger.info('world')






### if you want to also write logs to mongodb

connect_url = 'mongodb://myUserAdmin:8mwTdy1klnxxxx@112.25.53.14:27017/admin'
logger = LogManager('helloMongo').get_logger_and_add_handlers(mongo_url=connect_url)

logger.debug('hello')

logger.info('world')





### and also you can write log information to file