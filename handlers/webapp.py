
from aiogram import Router, F
from aiogram.types import CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from services.storage import storage
from handlers.start import get_text
from config import WEBAPP_URL

router = Router()


@router.callback_query(F.data == 'show_map')
async def show_map(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    exchangers = storage.get_exchangers()
    
    # Формируем URL для Web App с данными обменников
    webapp_url = WEBAPP_URL
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_open_map'),
                web_app=WebAppInfo(url=webapp_url)
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_id, 'btn_back'),
                callback_data="main_menu"
            )
        ]
    ])
    
    text = get_text(user_id, 'map_description', count=len(exchangers))
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()
