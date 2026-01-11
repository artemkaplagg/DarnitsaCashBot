import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, UPDATE_INTERVAL
from handlers import start_router, rates_router, alerts_router, admin_router
from handlers.webapp import router as webapp_router
from services.currency_api import currency_api
from services.storage import storage


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def update_rates_periodically():
    """
    Фоновая задача для обновления курсов валют каждые 5 минут
    """
    while True:
        try:
            logger.info("Обновление курсов валют...")
            
            rates = await currency_api.get_all_rates()
            
            if rates['USD']['monobank']:
                storage.save_rate(
                    'monobank', 
                    'USD',
                    rates['USD']['monobank']['buy'],
                    rates['USD']['monobank']['sell']
                )
                logger.info(f"USD сохранен: {rates['USD']['monobank']['buy']}/{rates['USD']['monobank']['sell']}")
            
            if rates['EUR']['monobank']:
                storage.save_rate(
                    'monobank',
                    'EUR',
                    rates['EUR']['monobank']['buy'],
                    rates['EUR']['monobank']['sell']
                )
                logger.info(f"EUR сохранен: {rates['EUR']['monobank']['buy']}/{rates['EUR']['monobank']['sell']}")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении курсов: {e}")
        
        await asyncio.sleep(UPDATE_INTERVAL)


async def check_alerts(bot: Bot):
    """
    Фоновая задача для проверки alerts пользователей
    """
    previous_rates = {}
    
    while True:
        try:
            await asyncio.sleep(300)
            
            rates = await currency_api.get_all_rates()
            all_alerts = storage.get_all_alerts()
            
            for user_id_str, user_alerts in all_alerts.items():
                user_id = int(user_id_str)
                lang = storage.get_user_language(user_id)
                
                for alert in user_alerts:
                    if not alert.get('active'):
                        continue
                    
                    currency = alert['currency']
                    alert_type = alert['type']
                    threshold = alert['threshold']
                    
                    current_rate = None
                    if rates[currency]['monobank']:
                        current_rate = rates[currency]['monobank']['sell']
                    
                    if not current_rate:
                        continue
                    
                    prev_rate = previous_rates.get(f"{user_id}_{currency}")
                    
                    if alert_type == 'percent' and prev_rate:
                        change_percent = abs((current_rate - prev_rate) / prev_rate * 100)
                        
                        if change_percent >= threshold:
                            direction = "зріс" if current_rate > prev_rate else "впав"
                            if lang == 'ru':
                                direction = "вырос" if current_rate > prev_rate else "упал"
                            
                            message = f"🔔 <b>Сповіщення про курс!</b>\n\n"
                            message += f"💱 {currency} {direction} на {change_percent:.2f}%\n\n"
                            message += f"Поточний курс: {current_rate:.2f} ₴"
                            
                            if lang == 'ru':
                                message = f"🔔 <b>Уведомление о курсе!</b>\n\n"
                                message += f"💱 {currency} {direction} на {change_percent:.2f}%\n\n"
                                message += f"Текущий курс: {current_rate:.2f} ₴"
                            
                            try:
                                await bot.send_message(
                                    user_id,
                                    message,
                                    parse_mode='HTML'
                                )
                            except Exception as e:
                                logger.error(f"Не удалось отправить alert пользователю {user_id}: {e}")
                    
                    previous_rates[f"{user_id}_{currency}"] = current_rate
            
        except Exception as e:
            logger.error(f"Ошибка при проверке alerts: {e}")


async def on_startup(bot: Bot):
    """
    Выполняется при запуске бота
    """
    logger.info("Бот запущен!")
    
    asyncio.create_task(update_rates_periodically())
    asyncio.create_task(check_alerts(bot))
    
    try:
        rates = await currency_api.get_all_rates()
        logger.info(f"Первоначальная загрузка курсов: USD={rates['USD']['monobank']}, EUR={rates['EUR']['monobank']}")
    except Exception as e:
        logger.error(f"Ошибка при первоначальной загрузке курсов: {e}")


async def on_shutdown(bot: Bot):
    """
    Выполняется при остановке бота
    """
    logger.info("Бот остановлен!")
    await bot.session.close()


async def main():
    """
    Главная функция запуска бота
    """
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage_fsm = MemoryStorage()
    dp = Dispatcher(storage=storage_fsm)
    
    dp.include_router(start_router)
    dp.include_router(rates_router)
    dp.include_router(alerts_router)
    dp.include_router(admin_router)
    dp.include_router(webapp_router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("Удаление webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Запуск polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")

