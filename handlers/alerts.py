
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.storage import storage
from handlers.start import get_text

router = Router()


@router.callback_query(F.data == 'show_alerts')
async def show_alerts_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Получаем алерты пользователя
    alerts = storage.get_user_alerts(user_id)
    
    keyboard_buttons = []
    
    if alerts:
        for alert in alerts:
            if alert.get('active'):
                currency = alert.get('currency')
                threshold = alert.get('threshold')
                alert_type = alert.get('type')
                
                if alert_type == 'percent':
                    text = f"🔔 {currency}: зміна >  {threshold}%"
                else:
                    text = f"🔔 {currency}: ціль {threshold} ₴"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f"alert_view_{alert['id']}"
                    )
                ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=get_text(user_id, 'btn_add_alert'),
            callback_data="alert_add"
        )
    ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=get_text(user_id, 'btn_back'),
            callback_data="main_menu"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    alerts_text = get_text(user_id, 'alerts_menu')
    
    if not alerts:
        alerts_text += f"\n\n<i>{get_text(user_id, 'no_alerts')}</i>"
    
    await callback.message.edit_text(
        alerts_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'alert_add')
async def alert_add_select_currency(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 USD", callback_data="alertnew_USD"),
            InlineKeyboardButton(text="💶 EUR", callback_data="alertnew_EUR")
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="show_alerts"
            )
        ]
    ])
    
    lang = storage.get_user_language(user_id)
    text = "Оберіть валюту:" if lang == 'uk' else "Выберите валюту:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('alertnew_'))
async def alert_add_type(callback: CallbackQuery):
    user_id = callback.from_user.id
    currency = callback.data.split('_')[1]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 При зміні на 1%",
                callback_data=f"alertcreate_{currency}_percent_1"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 При зміні на 2%",
                callback_data=f"alertcreate_{currency}_percent_2"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="alert_add"
            )
        ]
    ])
    
    lang = storage.get_user_language(user_id)
    text = f"Налаштування сповіщення для {currency}:" if lang == 'uk' else f"Настройка уведомления для {currency}:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('alertcreate_'))
async def alert_create(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    parts = callback.data.split('_')
    currency = parts[1]
    alert_type = parts[2]
    threshold = float(parts[3])
    
    # Создаём алерт
    storage.add_alert(user_id, currency, alert_type, threshold)
    
    lang = storage.get_user_language(user_id)
    success_text = f"✅ Сповіщення створено!\n\nВи отримаєте повідомлення, коли курс {currency} зміниться більше ніж на {threshold}%"
    
    if lang == 'ru':
        success_text = f"✅ Уведомление создано!\n\nВы получите сообщение, когда курс {currency} изменится более чем на {threshold}%"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="show_alerts"
            )
        ]
    ])
    
    await callback.message.edit_text(
        success_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('alert_view_'))
async def alert_view(callback: CallbackQuery):
    user_id = callback.from_user.id
    alert_id = int(callback.data.split('_')[2])
    
    alerts = storage.get_user_alerts(user_id)
    alert = next((a for a in alerts if a.get('id') == alert_id), None)
    
    if not alert:
        await callback.answer("❌ Сповіщення не знайдено")
        return
    
    lang = storage.get_user_language(user_id)
    
    text = f"🔔 <b>Деталі сповіщення</b>\n\n"
    text += f"💱 Валюта: {alert['currency']}\n"
    text += f"📊 Тип: {alert['type']}\n"
    text += f"📈 Поріг: {alert['threshold']}\n"
    
    if lang == 'ru':
        text = f"🔔 <b>Детали уведомления</b>\n\n"
        text += f"💱 Валюта: {alert['currency']}\n"
        text += f"📊 Тип: {alert['type']}\n"
        text += f"📈 Порог: {alert['threshold']}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗑 Видалити" if lang == 'uk' else "🗑 Удалить",
                callback_data=f"alert_delete_{alert_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="show_alerts"
            )
        ]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('alert_delete_'))
async def alert_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    alert_id = int(callback.data.split('_')[2])
    
    storage.delete_alert(user_id, alert_id)
    
    lang = storage.get_user_language(user_id)
    success_text = "✅ Сповіщення видалено" if lang == 'uk' else "✅ Уведомление удалено"
    
    await callback.answer(success_text)
    
    # Возвращаемся к списку алертов
    await show_alerts_menu(callback)
