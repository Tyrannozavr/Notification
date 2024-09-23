import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Создание директории для логов, если она не существует
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настройка логирования
logger = logging.getLogger('AppLogger')
logger.setLevel(logging.DEBUG)  # Уровень логирования

# Создание обработчика для ротации логов по времени (каждый день)
handler = TimedRotatingFileHandler(
    os.path.join(log_directory, 'app.log'),
    when='midnight',  # Ротация каждый день
    interval=1,
    backupCount=7  # Хранить 7 дней логов
)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Добавление обработчика к логгеру
logger.addHandler(handler)

def log_user_action(user_id, action):
    logger.info(f'User {user_id} performed action: {action}')

def log_error(error_message):
    logger.error(f'Error occurred: {error_message}')
