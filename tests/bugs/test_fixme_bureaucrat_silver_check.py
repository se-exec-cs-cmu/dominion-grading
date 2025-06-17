"""
Test for FIXME: card.py line 339 - Bureaucrat should check Silver availability
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

from dominion.game import DominionGame
from dominion.card import Card, VictoryCard
from dominion.controller import Controller


class MockController(Controller):
    """Mock controller that implements all required abstract methods"""
    def __init__(self, game):
        self.game = game
        self.card_picked = None
        
    @property
    def current_player(self):
        return self.game.current_player
        
    def trash(self, card):
        self.game.trash.append(card)
        
    def ask_yes_no(self, prompt):
        return False
        
    def pick_card_from_supply(self, maximum_cost=None):
        return None
        
    def pick_action(self, cards):
        return None
        
    def pick_cards_from_list(self, cards, minimum=0, maximum=None):
        return []
        
    def pick_cards_from_hand(self, player, minimum=0, maximum=None):
        return []
        
    def pick_card_from_list(self, cards):
        # For Bureaucrat, pick first victory card
        self.card_picked = cards[0] if cards else None
        return self.card_picked


def test_bureaucrat_with_silver_available():
    """Test Bureaucrat works normally when Silver is available"""
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Bureaucrat", "Market", "Smithy", "Village", "Cellar",
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    alice = game.current_player
    bob = game.players[1]
    
    # Ensure Silver is available
    initial_silver = game.supply.remaining("Silver")
    assert initial_silver > 0, "Test requires Silver in supply"
    
    # Give Bob a victory card in hand
    bob.hand.append(Card.create("Estate"))
    bob_initial_deck_size = len(bob.deck.cards)
    
    # Alice plays Bureaucrat
    bureaucrat = Card.create("Bureaucrat")
    alice.hand.append(bureaucrat)
    alice_initial_deck_size = len(alice.deck.cards)
    
    game.action(alice, bureaucrat)
    
    # Alice should have gained a Silver on top of deck
    assert len(alice.deck.cards) == alice_initial_deck_size + 1, \
        "Alice should have one more card in deck"
    assert alice.deck.cards[-1].name == "Silver", \
        "Silver should be on top of Alice's deck (last in list)"
    
    # Supply should have one less Silver
    assert game.supply.remaining("Silver") == initial_silver - 1, \
        "Supply should have one less Silver"
    
    # Bob should have put Estate on deck
    assert len(bob.deck.cards) == bob_initial_deck_size + 1, \
        "Bob should have one more card in deck"


def test_bureaucrat_with_no_silver_in_supply():
    """Test Bureaucrat when Silver pile is empty"""
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Bureaucrat", "Market", "Smithy", "Village", "Cellar",
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    alice = game.current_player
    bob = game.players[1]
    
    # Empty the Silver supply
    game.supply._card_name_to_remaining["Silver"] = 0
    
    # Give Bob a victory card
    bob.hand.append(Card.create("Estate"))
    bob_initial_deck_size = len(bob.deck.cards)
    
    # Alice plays Bureaucrat
    bureaucrat = Card.create("Bureaucrat")
    alice.hand.append(bureaucrat)
    alice_initial_deck_size = len(alice.deck.cards)
    
    # This should not raise any exceptions
    try:
        game.action(alice, bureaucrat)
    except ValueError as e:
        if "No more Silver cards in supply" in str(e):
            pytest.fail("Bureaucrat should handle empty Silver supply gracefully")
        raise  # Re-raise if it's a different ValueError
    
    # Alice should NOT have gained a Silver
    assert len(alice.deck.cards) == alice_initial_deck_size, \
        "Alice's deck size should not change when no Silver available"
    
    # Supply should still have 0 Silver
    assert game.supply.remaining("Silver") == 0, \
        "Silver supply should still be empty"
    
    # Attack portion should still work - Bob puts victory card on deck
    assert len(bob.deck.cards) == bob_initial_deck_size + 1, \
        "Bob should still be affected by attack portion"


def test_bureaucrat_with_one_silver_left():
    """Test Bureaucrat when exactly one Silver remains"""
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Bureaucrat", "Market", "Smithy", "Village", "Cellar",
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    alice = game.current_player
    
    # Set Silver supply to 1
    game.supply._card_name_to_remaining["Silver"] = 1
    
    # Alice plays Bureaucrat
    bureaucrat = Card.create("Bureaucrat")
    alice.hand.append(bureaucrat)
    alice_initial_deck_size = len(alice.deck.cards)
    
    game.action(alice, bureaucrat)
    
    # Alice should have gained the last Silver
    assert len(alice.deck.cards) == alice_initial_deck_size + 1, \
        "Alice should have gained a Silver"
    assert alice.deck.cards[-1].name == "Silver", \
        "Silver should be on top of deck"
    
    # Supply should now be empty
    assert game.supply.remaining("Silver") == 0, \
        "Silver supply should now be empty"


def test_bureaucrat_attack_still_works_without_silver():
    """Test that attack portion works even when Silver unavailable"""
    game = DominionGame.create(
        player_names=["Alice", "Bob", "Charlie"],
        kingdom_card_names=["Bureaucrat", "Market", "Smithy", "Village", "Cellar",
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    alice = game.current_player
    bob = game.players[1]
    charlie = game.players[2]
    
    # No Silver in supply
    game.supply._card_name_to_remaining["Silver"] = 0
    
    # Give other players victory cards
    bob.hand.extend([Card.create("Estate"), Card.create("Market")])
    charlie.hand.extend([Card.create("Duchy"), Card.create("Smithy")])
    
    bob_initial_deck = len(bob.deck.cards)
    charlie_initial_deck = len(charlie.deck.cards)
    
    # Play Bureaucrat
    bureaucrat = Card.create("Bureaucrat")
    alice.hand.append(bureaucrat)
    
    # This should not raise any exceptions
    try:
        game.action(alice, bureaucrat)
    except ValueError as e:
        if "No more Silver cards in supply" in str(e):
            pytest.fail("Bureaucrat should handle empty Silver supply gracefully")
        raise  # Re-raise if it's a different ValueError
    
    # Both other players should still be affected
    assert len(bob.deck.cards) == bob_initial_deck + 1, \
        "Bob should put victory card on deck"
    assert len(charlie.deck.cards) == charlie_initial_deck + 1, \
        "Charlie should put victory card on deck"


def test_bureaucrat_does_not_crash_on_error():
    """Test Bureaucrat handles supply.draw() errors gracefully"""
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Bureaucrat", "Market", "Smithy", "Village", "Cellar",
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    alice = game.current_player
    
    # Empty the Silver supply
    game.supply._card_name_to_remaining["Silver"] = 0
    
    # Play Bureaucrat
    bureaucrat = Card.create("Bureaucrat")
    alice.hand.append(bureaucrat)
    
    # This should not raise any exceptions
    try:
        game.action(alice, bureaucrat)
    except ValueError as e:
        if "No more Silver cards in supply" in str(e):
            pytest.fail("Bureaucrat should handle empty Silver supply gracefully")
        raise  # Re-raise if it's a different ValueError