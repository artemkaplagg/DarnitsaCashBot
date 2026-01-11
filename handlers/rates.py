from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from services.currency_api import currency_api
from services.storage import storage
from services.charts import chart_generator
from handlers.start import get_text
from datetime import datetime, timedelta

router = Router()


def get_back_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="main_menu"
            )
        ]
    ])


@router.callback_query(F.data == 'show_rates')
async def show_current_rates(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    await callback.answer("⏳ Оновлюю курси...")
    
    try:
        rates = await currency_api.get_all_rates()
        
        # Получаем историю для расчета изменений за 2 часа
        usd_history = storage.get_rate_history('USD', 'monobank', hours=2)
        eur_history = storage.get_rate_history('EUR', 'monobank', hours=2)
        
        # Рассчитываем изменение
        usd_change = 0
        eur_change = 0
        
        if len(usd_history) > 1:
            usd_old = usd_history[0]['sell']
            usd_new = rates['USD']['monobank'].get('sell', 0)
            usd_change = round(usd_new - usd_old, 2) if usd_new else 0
        
        if len(eur_history) > 1:
            eur_old = eur_history[0]['sell']
            eur_new = rates['EUR']['monobank'].get('sell', 0)
            eur_change = round(eur_new - eur_old, 2) if eur_new else 0
        
        # Эмодзи тренда
        usd_emoji = currency_api.get_trend_emoji(usd_change)
        eur_emoji = currency_api.get_trend_emoji(eur_change)
        
        # Форматируем сообщение
        text = get_text(user_id, 'current_rates', time=rates['timestamp'])
        
        # USD блок
        text += f"💵 <b>{get_text(user_id, 'usd')}</b>\n"
        text += f"┣ <b>{get_text(user_id, 'nbu')}:</b> {rates['USD']['nbu']:.2f} ₴\n" if rates['USD']['nbu'] else ""
        
        if rates['USD']['monobank']:
            text += f"┣ <b>Monobank:</b>\n"
            text += f"┃  ├ {get_text(user_id, 'buy')}: <code>{rates['USD']['monobank']['buy']:.2f}</code> ₴\n"
            text += f"┃  └ {get_text(user_id, 'sell')}: <code>{rates['USD']['monobank']['sell']:.2f}</code> ₴\n"
        
        if rates['USD']['privatbank']:
            text += f"┗ <b>PrivatBank:</b>\n"
            text += f"   ├ {get_text(user_id, 'buy')}: <code>{rates['USD']['privatbank']['buy']:.2f}</code> ₴\n"
            text += f"   └ {get_text(user_id, 'sell')}: <code>{rates['USD']['privatbank']['sell']:.2f}</code> ₴\n"
        
        if usd_change != 0:
            change_sign = "+" if usd_change > 0 else ""
            text += f"📊 {get_text(user_id, 'change_2h')}: {usd_emoji} {change_sign}{usd_change:.2f} ₴\n"
        
        text += "\n"
        
        # EUR блок
        text += f"💶 <b>{get_text(user_id, 'eur')}</b>\n"
        text += f"┣ <b>{get_text(user_id, 'nbu')}:</b> {rates['EUR']['nbu']:.2f} ₴\n" if rates['EUR']['nbu'] else ""
        
        if rates['EUR']['monobank']:
            text += f"┣ <b>Monobank:</b>\n"
            text += f"┃  ├ {get_text(user_id, 'buy')}: <code>{rates['EUR']['monobank']['buy']:.2f}</code> ₴\n"
            text += f"┃  └ {get_text(user_id, 'sell')}: <code>{rates['EUR']['monobank']['sell']:.2f}</code> ₴\n"
        
        if rates['EUR']['privatbank']:
            text += f"┗ <b>PrivatBank:</b>\n"
            text += f"   ├ {get_text(user_id, 'buy')}: <code>{rates['EUR']['privatbank']['buy']:.2f}</code> ₴\n"
            text += f"   └ {get_text(user_id, 'sell')}: <code>{rates['EUR']['privatbank']['sell']:.2f}</code> ₴\n"
        
        if eur_change != 0:
            change_sign = "+" if eur_change > 0 else ""
            text += f"📊 {get_text(user_id, 'change_2h')}: {eur_emoji} {change_sign}{eur_change:.2f} ₴\n"
        
        # Сохраняем в историю
        if rates['USD']['monobank']:
            storage.save_rate('monobank', 'USD', 
                            rates['USD']['monobank']['buy'],
                            rates['USD']['monobank']['sell'])
        
        if rates['EUR']['monobank']:
            storage.save_rate('monobank', 'EUR',
                            rates['EUR']['monobank']['buy'],
                            rates['EUR']['monobank']['sell'])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(user_id, 'btn_chart'),
                    callback_data="show_chart_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(user_id, 'btn_back'),
                    callback_data="main_menu"
                )
            ]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.message.edit_text(
            get_text(user_id, 'error', error=str(e)),
            reply_markup=get_back_keyboard(user_id),
            parse_mode='HTML'
        )


@router.callback_query(F.data == 'show_chart_menu')
async def show_chart_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 USD", callback_data="chart_USD"),
            InlineKeyboardButton(text="💶 EUR", callback_data="chart_EUR")
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(
        get_text(user_id, 'select_currency_chart'),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('chart_'))
async def select_chart_currency(callback: CallbackQuery):
    user_id = callback.from_user.id
    currency = callback.data.split('_')[1]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'period_day'),
                callback_data=f"chartgen_{currency}_day"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'period_week'),
                callback_data=f"chartgen_{currency}_week"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'period_month'),
                callback_data=f"chartgen_{currency}_month"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="show_chart_menu"
            )
        ]
    ])
    
    await callback.message.edit_text(
        get_text(user_id, 'select_period'),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('chartgen_'))
async def generate_chart(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    parts = callback.data.split('_')
    currency = parts[1]
    period = parts[2]
    
    await callback.answer(get_text(user_id, 'generating_chart'))
    
    try:
        # Получаем данные из истории
        hours_map = {'day': 24, 'week': 168, 'month': 720}
        hours = hours_map.get(period, 24)
        
        history = storage.get_rate_history(currency, 'monobank', hours=hours)
        
        if not history or len(history) < 2:
            await callback.message.answer(
                f"❌ Недостатньо даних для побудови графіка {currency}",
                parse_mode='HTML'
            )
            return
        
        # Генерируем график
        chart_buffer = chart_generator.generate_rate_chart(currency, history, period)
        
        # Отправляем как фото
        photo = BufferedInputFile(chart_buffer.read(), filename=f"{currency}_{period}.png")
        
        period_names = {'day': 'день', 'week': 'тиждень', 'month': 'місяць'}
        caption = get_text(user_id, 'chart_caption', 
                         currency=currency, 
                         period=period_names.get(period, period))
        
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.message.answer(
            get_text(user_id, 'error', error=str(e)),
            parse_mode='HTML'
        )

