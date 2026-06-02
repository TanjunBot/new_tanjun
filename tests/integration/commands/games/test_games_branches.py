from locale_keys import locale
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from commands.games.akinator import akinator
from commands.games.connect4 import Connect4, connect4
from commands.games.flag_quiz import flag_quiz
from commands.games.hangman import get_guessed_letters, hangman, wrong_letters
from commands.games.rps import rps
from commands.games.tic_tac_toe import tic_tac_toe
from commands.games.wordle import wordle
from tests.helpers.discord import make_member, make_target_member
pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize('locale,expected', [('de', 'de'), ('fr', 'fr'), ('ja', 'jp'), ('pt-BR', 'pt'), ('en-US', 'en')])
@patch('commands.games.akinator.Akinator')
async def test_akinator_locales(mock_cls, admin_command_info, locale, expected):
    mock_aki = MagicMock()
    mock_aki.start_game = MagicMock()
    mock_cls.return_value = mock_aki
    admin_command_info.locale = locale
    await akinator(admin_command_info, theme='Characters')
    mock_cls.assert_called_once()
    assert mock_cls.call_args.kwargs.get('lang') == expected or mock_cls.call_args[1].get('lang') == expected

@patch('commands.games.akinator.Akinator')
async def test_akinator_starts_game(mock_cls, admin_command_info):
    mock_aki = MagicMock()
    mock_aki.start_game = MagicMock()
    mock_aki.question = 'Is it human?'
    mock_cls.return_value = mock_aki
    await akinator(admin_command_info, None)
    admin_command_info.reply.assert_awaited_once()

def test_connect4_check_winner_horizontal():
    game = Connect4(make_member(), locale='en')
    for col in range(4):
        game.board[5][col] = game.player1_move
    assert game.check_winner() == game.player1_move

def test_connect4_check_winner_vertical():
    game = Connect4(make_member(), locale='en')
    for row in range(4):
        game.board[row][0] = game.player2_move
    assert game.check_winner() == game.player2_move

def test_connect4_is_full():
    game = Connect4(make_member(), locale='en')
    for row in range(game.rows):
        for col in range(game.columns):
            game.board[row][col] = game.player1_move
    assert game.is_full() is True

def test_connect4_available_moves():
    game = Connect4(make_member(), locale='en')
    game.board[5][0] = game.player1_move
    moves = game.get_available_moves()
    assert all((isinstance(m, tuple) for m in moves))

@patch('commands.games.connect4.Connect4.update_board', new_callable=AsyncMock)
async def test_connect4_command(mock_update, admin_command_info):
    await connect4(admin_command_info, admin_command_info.user, make_target_member())
    mock_update.assert_awaited_once()

@patch('commands.games.hangman.random.choice', return_value='test')
async def test_hangman_starts(mock_choice, admin_command_info):
    await hangman(admin_command_info, language='en')
    admin_command_info.reply.assert_awaited_once()

def test_hangman_guessed_letters():
    assert get_guessed_letters(['t', 'e'], 'test') == 'te_t'
    assert get_guessed_letters(['test'], 'test') == 'test'

def test_hangman_wrong_letters():
    assert wrong_letters(['a', 'b', 'test'], 'test') == 2

@patch('commands.games.rps.random.choice', return_value='rock')
async def test_rps_vs_bot(mock_choice, admin_command_info):
    await rps(admin_command_info, make_target_member())
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get('view') is not None

async def test_rps_vs_bot_user(admin_command_info):
    bot = make_target_member()
    bot.bot = True
    with patch('commands.games.rps.random.choice', return_value='rock'):
        await rps(admin_command_info, bot)
    admin_command_info.reply.assert_awaited_once()

@patch('commands.games.tic_tac_toe.TicTacToe.update_board', new_callable=AsyncMock)
async def test_tic_tac_toe_starts(mock_update, admin_command_info):
    await tic_tac_toe(admin_command_info, admin_command_info.user, make_target_member())
    mock_update.assert_awaited_once()

@patch('commands.games.wordle.random.choice', return_value='apple')
async def test_wordle_starts(mock_choice, admin_command_info):
    await wordle(admin_command_info, language='en')
    admin_command_info.reply.assert_awaited_once()

@patch('commands.games.flag_quiz.random_flag', return_value='United_States.png')
async def test_flag_quiz_starts(mock_flag, admin_command_info):
    await flag_quiz(admin_command_info)
    admin_command_info.reply.assert_awaited_once()