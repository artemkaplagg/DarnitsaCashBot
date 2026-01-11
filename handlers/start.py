
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from services.storage import storage
import json
import os

router = Router()

# Загрузка локалей
def load_locale(lang: str) -> dict:
    locale_path = os.path.join('locales', f'{lang}.json')
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_text(user_id: int, key: str, **kwargs) -> str:
    lang = storage.get_user_language(user_id)
    locale = load_locale(lang)
    text = locale.get(key, key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text

def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])
    return keyboard

def get_main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_rates'),
                callback_data="show_rates"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_chart'),
                callback_data="show_chart_menu"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_map'),
                callback_data="show_map"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_alerts'),
                callback_data="show_alerts"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_settings'),
                callback_data="show_settings"
            )
        ]
    ])
    return keyboard


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли уже язык у пользователя
    lang = storage.get_user_language(user_id)
    
    if lang == 'uk':  # Дефолтное значение означает, что пользователь новый
        # Новый пользователь - предлагаем выбрать язык
        welcome_text = "👋 <b>Вітаємо в Currency Дарницький 2.0!</b>\n\n💰 Бот для моніторингу курсів валют у режимі реального часу\n\n🔹 Офіційні курси НБУ\n🔹 Банківські курси (Monobank, PrivatBank)\n🔹 Карта обмінників Дарницького району\n🔹 Графіки динаміки валют\n🔹 Сповіщення про зміни курсу\n\n<b>Оберіть мову / Выберите язык:</b>"
        
        await message.answer(
            welcome_text,
            reply_markup=get_language_keyboard(),
            parse_mode='HTML'
        )
    else:
        # Пользователь уже есть - показываем главное меню
        await message.answer(
            get_text(user_id, 'main_menu'),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode='HTML'
        )


@router.callback_query(F.data.startswith('lang_'))
async def select_language(callback: CallbackQuery):
    lang = callback.data.split('_')[1]
    user_id = callback.from_user.id
    
    storage.set_user_language(user_id, lang)
    
    await callback.message.edit_text(
        get_text(user_id, 'language_selected'),
        parse_mode='HTML'
    )
    
    # Показываем главное меню
    await callback.message.answer(
        get_text(user_id, 'main_menu'),
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'main_menu')
async def back_to_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    await callback.message.edit_text(
        get_text(user_id, 'main_menu'),
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'show_settings')
async def show_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = storage.get_user_language(user_id)
    
    settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🇺🇦 Українська" if lang == 'uk' else "🇷🇺 Русский",
                callback_data="change_language"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="main_menu"
            )
        ]
    ])
    
    settings_text = get_text(user_id, 'main_menu').replace('Головне меню', 'Налаштування').replace('Главное меню', 'Настройки')
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=settings_keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()


@router.callback_query(F.data == 'change_language')
async def change_language(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Оберіть мову / Выберите язык:</b>",
        reply_markup=get_language_keyboard(),
        parse_mode='HTML'
    )
    
    await callback.answer()
