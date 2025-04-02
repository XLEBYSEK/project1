import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния игрового поля
EMPTY = 0
CROSS = 1
CIRCLE = 2

# Словарь для хранения игровых досок
games = {}

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    update.message.reply_text(f"Привет, {user.first_name}! Я бот для игры в крестики-нолики. "
                             "Используй /newgame чтобы начать новую игру.")

def new_game(update: Update, context: CallbackContext) -> None:
    """Создание новой игры"""
    chat_id = update.effective_chat.id
    games[chat_id] = {
        'board': [EMPTY] * 9,
        'current_player': CROSS,
        'winner': None
    }
    
    # Создаем клавиатуру с игровым полем
    keyboard = create_keyboard(chat_id)
    update.message.reply_text('Новая игра! Ходят крестики (X).', reply_markup=keyboard)

def create_keyboard(chat_id):
    """Создает клавиатуру с текущим состоянием доски"""
    board = games[chat_id]['board']
    keyboard = []
    
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i + j]
            if cell == EMPTY:
                text = ' '
            elif cell == CROSS:
                text = '❌'
            else:
                text = '⭕'
            row.append(InlineKeyboardButton(text, callback_data=str(i + j)))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def button_click(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатия на кнопку"""
    query = update.callback_query
    chat_id = query.message.chat_id
    data = int(query.data)
    
    # Проверяем, есть ли активная игра
    if chat_id not in games:
        query.answer(text="Нет активной игры. Начните новую с помощью /newgame")
        return
    
    game = games[chat_id]
    
    # Проверяем, закончена ли игра
    if game['winner'] is not None:
        query.answer(text="Игра уже завершена. Начните новую с помощью /newgame")
        return
    
    # Проверяем, можно ли сделать ход в выбранную клетку
    if game['board'][data] != EMPTY:
        query.answer(text="Эта клетка уже занята!")
        return
    
    # Делаем ход
    game['board'][data] = game['current_player']
    
    # Проверяем, есть ли победитель
    winner = check_winner(game['board'])
    if winner is not None:
        game['winner'] = winner
        winner_text = "Крестики (X) победили!" if winner == CROSS else "Нолики (O) победили!"
        query.edit_message_text(text=winner_text, reply_markup=create_keyboard(chat_id))
        return
    elif EMPTY not in game['board']:
        # Ничья
        game['winner'] = 'draw'
        query.edit_message_text(text="Ничья!", reply_markup=create_keyboard(chat_id))
        return
    
    # Меняем игрока
    game['current_player'] = CIRCLE if game['current_player'] == CROSS else CROSS
    player_text = "Ходят нолики (O)" if game['current_player'] == CIRCLE else "Ходят крестики (X)"
    query.edit_message_text(text=player_text, reply_markup=create_keyboard(chat_id))

def check_winner(board):
    """Проверяет, есть ли победитель"""
    # Все возможные выигрышные комбинации
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # горизонтали
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # вертикали
        [0, 4, 8], [2, 4, 6]              # диагонали
    ]
    
    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != EMPTY:
            return board[combo[0]]
    
    return None

def main() -> None:
    """Запуск бота"""
    # Замените 'YOUR_TOKEN' на токен вашего бота
    updater = Updater("YOUR_TOKEN")
    
    # Регистрируем обработчики
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("newgame", new_game))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click))
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
