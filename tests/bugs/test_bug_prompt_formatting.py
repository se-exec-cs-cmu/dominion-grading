import pytest
from unittest.mock import Mock

from dominion.controller import CliController
from dominion.card import Card, Copper # Importing Copper for a dummy card
from dominion.cli import DominionCLI

# Dummy Card class for testing purposes
class DummyCard(Card):
    def __init__(self, name="Dummy", cost=0):
        self._name = name
        self._cost = cost

    @property
    def cost(self) -> int:
        return self._cost

    @property
    def name(self) -> str:
        return self._name

class MockGame:
    # Minimal mock for testing purposes that doesn't need full game init
    def __init__(self):
        self.current_player = Mock()
        self.current_player.hand = [DummyCard("Copper"), DummyCard("Estate")]

def test_pick_cards_from_list_prompt_formatting():
    """Test that pick_cards_from_list correctly formats prompts."""

    mock_cli = Mock(spec=DominionCLI)
    mock_cli.ask.return_value = "0" # Simulate picking the first card
    mock_cli.bold.side_effect = print # For debugging: print bold calls

    mock_game = MockGame()
    controller = CliController(cli=mock_cli, game=mock_game)

    test_cards = [DummyCard(f"Card{i}") for i in range(5)]

    # Test case 1: minimum == maximum
    controller.pick_cards_from_list(test_cards, minimum=1, maximum=1)
    # Check the last call to cli.bold
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick exactly 1 card from the following:" in called_prompt
    assert "{minimum}" not in called_prompt

    mock_cli.bold.reset_mock()

    # Test case 2: minimum >= 0 and maximum is not None (range)
    controller.pick_cards_from_list(test_cards, minimum=1, maximum=3)
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick between 1 and 3 cards from the following:" in called_prompt
    assert "{minimum}" not in called_prompt
    assert "{maximum}" not in called_prompt

    mock_cli.bold.reset_mock()

    # Test case 3: minimum == 0 and maximum is not None (at most)
    controller.pick_cards_from_list(test_cards, minimum=0, maximum=2)
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick at most 2 cards from the following:" in called_prompt
    assert "{maximum}" not in called_prompt

    mock_cli.bold.reset_mock()

    # Test case 4: minimum == 0 and maximum is None (any number)
    controller.pick_cards_from_list(test_cards, minimum=0, maximum=None)
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick any number of cards from the following:" in called_prompt

    mock_cli.bold.reset_mock()

    # Test case 5: minimum > 0 and maximum is None (at least)
    controller.pick_cards_from_list(test_cards, minimum=2, maximum=None)
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick at least 2 cards from the following:" in called_prompt
    assert "{minimum}" not in called_prompt

    # Test the pick_cards_from_hand method as well, as it calls pick_cards_from_list
    mock_cli.bold.reset_mock()
    controller.pick_cards_from_hand(mock_game.current_player, minimum=1, maximum=1)
    called_prompt = mock_cli.bold.call_args[0][0]
    assert "Pick exactly 1 card from the following:" in called_prompt
    assert "{minimum}" not in called_prompt 