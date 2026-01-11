from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.storage import storage
from handlers.start import get_text
from config import ADMIN_ID

router = Router()


class AdminStates(StatesGroup):
    waiting_exchanger_name = State()
    waiting_exchanger_address = State()
    waiting_exchanger_district = State()
    waiting_exchanger_coords = State()
    waiting_exchanger_phone = State()
    
    waiting_rate_exchanger_id = State()
    waiting_rate_currency = State()
    waiting_rate_buy = State()
    waiting_rate_sell = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def get_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_add_exchanger'),
                callback_data="admin_add_exchanger"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_update_rate'),
                callback_data="admin_update_rate"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_list_exchangers'),
                callback_data="admin_list_exchangers"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_stats'),
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="main_menu"
            )
        ]
    ])


@router.message(Command('admin'))
async def cmd_admin(message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас немає доступу до адмін-панелі")
        return
    
    users_count = len(storage.get_all_users())
    alerts_count = sum(len(alerts) for alerts in storage.get_all_alerts().values())
    exchangers_count = len(storage.get_exchangers())
    
    text = get_text(user_id, 'admin_panel',
                   users=users_count,
                   alerts=alerts_count,
                   exchangers=exchangers_count)
    
    await message.answer(
        text,
        reply_markup=get_admin_keyboard(user_id),
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'admin_stats')
async def admin_show_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Доступ заборонено")
        return
    
    users = storage.get_all_users()
    all_alerts = storage.get_all_alerts()
    exchangers = storage.get_exchangers()
    
    # Собираем статистику по языкам
    lang_stats = {'uk': 0, 'ru': 0}
    for uid in users:
        lang = storage.get_user_language(uid)
        lang_stats[lang] = lang_stats.get(lang, 0) + 1
    
    # Статистика по обменникам с курсами
    exchangers_with_rates = 0
    for ex in exchangers:
        if any(ex['rates'][curr]['buy'] is not None for curr in ['USD', 'EUR']):
            exchangers_with_rates += 1
    
    lang = storage.get_user_language(user_id)
    
    text = "📊 <b>Детальна статистика</b>\n\n" if lang == 'uk' else "📊 <b>Подробная статистика</b>\n\n"
    
    text += f"👥 <b>Користувачі:</b> {len(users)}\n" if lang == 'uk' else f"👥 <b>Пользователи:</b> {len(users)}\n"
    text += f"   ├ 🇺🇦 Українська: {lang_stats.get('uk', 0)}\n"
    text += f"   └ 🇷🇺 Русский: {lang_stats.get('ru', 0)}\n\n"
    
    text += f"💱 <b>Обмінники:</b> {len(exchangers)}\n" if lang == 'uk' else f"💱 <b>Обменники:</b> {len(exchangers)}\n"
    text += f"   └ З курсами: {exchangers_with_rates}\n\n" if lang == 'uk' else f"   └ С курсами: {exchangers_with_rates}\n\n"
    
    text += f"🔔 <b>Активні сповіщення:</b> {sum(len(a) for a in all_alerts.values())}\n" if lang == 'uk' else f"🔔 <b>Активные уведомления:</b> {sum(len(a) for a in all_alerts.values())}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="admin_back"
            )
        ]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'admin_back')
async def admin_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    users_count = len(storage.get_all_users())
    alerts_count = sum(len(alerts) for alerts in storage.get_all_alerts().values())
    exchangers_count = len(storage.get_exchangers())
    
    text = get_text(user_id, 'admin_panel',
                   users=users_count,
                   alerts=alerts_count,
                   exchangers=exchangers_count)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_keyboard(user_id),
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'admin_list_exchangers')
async def admin_list_exchangers(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Доступ заборонено")
        return
    
    exchangers = storage.get_exchangers()
    lang = storage.get_user_language(user_id)
    
    text = "📋 <b>Список обмінників:</b>\n\n" if lang == 'uk' else "📋 <b>Список обменников:</b>\n\n"
    
    for ex in exchangers:
        text += f"🏢 <b>{ex['name']}</b>\n"
        text += f"   📍 {ex['address']}\n"
        text += f"   📌 {ex['district']}\n"
        
        # Курсы USD
        if ex['rates']['USD']['buy']:
            text += f"   💵 USD: {ex['rates']['USD']['buy']:.2f} / {ex['rates']['USD']['sell']:.2f}\n"
        
        # Курсы EUR
        if ex['rates']['EUR']['buy']:
            text += f"   💶 EUR: {ex['rates']['EUR']['buy']:.2f} / {ex['rates']['EUR']['sell']:.2f}\n"
        
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="admin_back"
            )
        ]
    ])
    
    # Если текст слишком длинный, разбиваем на части
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await callback.message.answer(part, parse_mode='HTML', reply_markup=keyboard)
            else:
                await callback.message.answer(part, parse_mode='HTML')
    else:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    await callback.answer()


@router.callback_query(F.data == 'admin_update_rate')
async def admin_update_rate_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Доступ заборонено")
        return
    
    exchangers = storage.get_exchangers()
    
    keyboard_buttons = []
    for ex in exchangers:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{ex['name']} - {ex['district']}",
                callback_data=f"adminrate_ex_{ex['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=get_text(user_id, 'btn_back'),
            callback_data="admin_back"
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    lang = storage.get_user_language(user_id)
    text = "Оберіть обмінник:" if lang == 'uk' else "Выберите обменник:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith('adminrate_ex_'))
async def admin_update_rate_select_currency(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    exchanger_id = int(callback.data.split('_')[2])
    
    await state.update_data(exchanger_id=exchanger_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 USD", callback_data="adminrate_curr_USD"),
            InlineKeyboardButton(text="💶 EUR", callback_data="adminrate_curr_EUR")
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="admin_update_rate"
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


@router.callback_query(F.data.startswith('adminrate_curr_'))
async def admin_update_rate_enter_buy(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    currency = callback.data.split('_')[2]
    
    await state.update_data(currency=currency)
    await state.set_state(AdminStates.waiting_rate_buy)
    
    lang = storage.get_user_language(user_id)
    text = f"Введіть курс КУПІВЛІ {currency}:" if lang == 'uk' else f"Введите курс ПОКУПКИ {currency}:"
    
    await callback.message.edit_text(text, parse_mode='HTML')
    await callback.answer()


@router.message(AdminStates.waiting_rate_buy)
async def admin_update_rate_get_buy(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        buy_rate = float(message.text.replace(',', '.'))
        await state.update_data(buy_rate=buy_rate)
        await state.set_state(AdminStates.waiting_rate_sell)
        
        data = await state.get_data()
        currency = data['currency']
        
        lang = storage.get_user_language(user_id)
        text = f"Введіть курс ПРОДАЖУ {currency}:" if lang == 'uk' else f"Введите курс ПРОДАЖИ {currency}:"
        
        await message.answer(text)
        
    except ValueError:
        lang = storage.get_user_language(user_id)
        error_text = "❌ Невірний формат. Введіть число (наприклад: 40.50)" if lang == 'uk' else "❌ Неверный формат. Введите число (например: 40.50)"
        await message.answer(error_text)


@router.message(AdminStates.waiting_rate_sell)
async def admin_update_rate_get_sell(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        sell_rate = float(message.text.replace(',', '.'))
        
        data = await state.get_data()
        exchanger_id = data['exchanger_id']
        currency = data['currency']
        buy_rate = data['buy_rate']
        
        # Обновляем курс в базе
        storage.update_exchanger_rate(exchanger_id, currency, buy_rate, sell_rate)
        
        exchanger = storage.get_exchanger_by_id(exchanger_id)
        
        lang = storage.get_user_language(user_id)
        success_text = f"✅ <b>Курс оновлено!</b>\n\n"
        success_text += f"🏢 {exchanger['name']}\n"
        success_text += f"💱 {currency}\n"
        success_text += f"├ Купівля: {buy_rate:.2f} ₴\n"
        success_text += f"└ Продаж: {sell_rate:.2f} ₴"
        
        if lang == 'ru':
            success_text = f"✅ <b>Курс обновлен!</b>\n\n"
            success_text += f"🏢 {exchanger['name']}\n"
            success_text += f"💱 {currency}\n"
            success_text += f"├ Покупка: {buy_rate:.2f} ₴\n"
            success_text += f"└ Продажа: {sell_rate:.2f} ₴"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Оновити ще один" if lang == 'uk' else "✏️ Обновить еще один",
                    callback_data="admin_update_rate"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(user_id, 'btn_back'),
                    callback_data="admin_back"
                )
            ]
        ])
        
        await message.answer(
            success_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        lang = storage.get_user_language(user_id)
        error_text = "❌ Невірний формат. Введіть число (наприклад: 40.50)" if lang == 'uk' else "❌ Неверный формат. Введите число (например: 40.50)"
        await message.answer(error_text)


@router.callback_query(F.data == 'admin_add_exchanger')
async def admin_add_exchanger_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("❌ Доступ заборонено")
        return
    
    lang = storage.get_user_language(user_id)
    text = "Введіть назву обмінника:" if lang == 'uk' else "Введите название обменника:"
    
    await callback.message.edit_text(text, parse_mode='HTML')
    await state.set_state(AdminStates.waiting_exchanger_name)
    await callback.answer()


@router.message(AdminStates.waiting_exchanger_name)
async def admin_add_exchanger_get_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.waiting_exchanger_address)
    
    lang = storage.get_user_language(user_id)
    text = "Введіть адресу:" if lang == 'uk' else "Введите адрес:"
    
    await message.answer(text)


@router.message(AdminStates.waiting_exchanger_address)
async def admin_add_exchanger_get_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.update_data(address=message.text)
    await state.set_state(AdminStates.waiting_exchanger_district)
    
    lang = storage.get_user_language(user_id)
    text = "Введіть район (наприклад: Позняки):" if lang == 'uk' else "Введите район (например: Позняки):"
    
    await message.answer(text)


@router.message(AdminStates.waiting_exchanger_district)
async def admin_add_exchanger_get_district(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.update_data(district=message.text)
    await state.set_state(AdminStates.waiting_exchanger_coords)
    
    lang = storage.get_user_language(user_id)
    text = "Введіть координати (формат: 50.4165, 30.6327):" if lang == 'uk' else "Введите координаты (формат: 50.4165, 30.6327):"
    
    await message.answer(text)


@router.message(AdminStates.waiting_exchanger_coords)
async def admin_add_exchanger_get_coords(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        coords = message.text.replace(' ', '').split(',')
        lat = float(coords[0])
        lon = float(coords[1])
        
        await state.update_data(lat=lat, lon=lon)
        await state.set_state(AdminStates.waiting_exchanger_phone)
        
        lang = storage.get_user_language(user_id)
        text = "Введіть телефон (або - для пропуску):" if lang == 'uk' else "Введите телефон (или - для пропуска):"
        
        await message.answer(text)
        
    except (ValueError, IndexError):
        lang = storage.get_user_language(user_id)
        error_text = "❌ Невірний формат. Спробуйте ще раз (наприклад: 50.4165, 30.6327)" if lang == 'uk' else "❌ Неверный формат. Попробуйте еще раз (например: 50.4165, 30.6327)"
        await message.answer(error_text)


@router.message(AdminStates.waiting_exchanger_phone)
async def admin_add_exchanger_get_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    phone = message.text if message.text != '-' else ''
    
    data = await state.get_data()
    
    # Добавляем обменник
    new_exchanger = storage.add_exchanger(
        name=data['name'],
        address=data['address'],
        district=data['district'],
        lat=data['lat'],
        lon=data['lon'],
        phone=phone
    )
    
    lang = storage.get_user_language(user_id)
    success_text = f"✅ <b>Обмінник додано!</b>\n\n"
    success_text += f"🏢 {new_exchanger['name']}\n"
    success_text += f"📍 {new_exchanger['address']}\n"
    success_text += f"📌 {new_exchanger['district']}\n"
    success_text += f"🌍 {new_exchanger['lat']}, {new_exchanger['lon']}\n"
    
    if phone:
        success_text += f"📞 {phone}\n"
    
    if lang == 'ru':
        success_text = f"✅ <b>Обменник добавлен!</b>\n\n"
        success_text += f"🏢 {new_exchanger['name']}\n"
        success_text += f"📍 {new_exchanger['address']}\n"
        success_text += f"📌 {new_exchanger['district']}\n"
        success_text += f"🌍 {new_exchanger['lat']}, {new_exchanger['lon']}\n"
        
        if phone:
            success_text += f"📞 {phone}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="admin_back"
            )
        ]
    ])
    
    await message.answer(
        success_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await state.clear()

