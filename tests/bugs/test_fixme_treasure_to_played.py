"""
Test for FIXME: game.py line 84 - treasure cards should be moved to played pile
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

from dominion.game import DominionGame, Phase
from dominion.card import Card, TreasureCard, Copper, Silver, Gold, ActionCard
from dominion.controller import Controller


class MockController(Controller):
    """Mock controller that implements all required abstract methods"""
    def __init__(self, game):
        self.game = game
        
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


def test_treasures_moved_to_played_when_entering_buy_phase():
    """Test that treasure cards are moved to played pile when transitioning to buy phase"""
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Market", "Smithy", "Village", "Cellar", "Workshop",
                           "Chapel", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    player = game.current_player
    
    # Set up hand with mix of treasures and non-treasures
    player.hand = [
        Card.create("Copper"),
        Card.create("Silver"),
        Card.create("Gold"),
        Card.create("Estate"),  # Not a treasure
        Card.create("Market")   # Not a treasure
    ]
    
    # Clear played pile
    player.played = []
    
    # Player has no actions (to trigger transition to buy phase)
    player.actions = 0
    
    # Check phase transition
    assert game.phase == Phase.ACTION
    game.check_for_end_of_phase()
    
    # Should now be in buy phase
    assert game.phase == Phase.BUY, "Should have transitioned to buy phase"
    
    # All treasures should be in played pile
    assert len(player.played) == 3, f"Should have 3 treasures in played pile, but has {len(player.played)}"
    
    # Check specific cards
    played_names = [card.name for card in player.played]
    assert "Copper" in played_names, "Copper should be in played pile"
    assert "Silver" in played_names, "Silver should be in played pile"
    assert "Gold" in played_names, "Gold should be in played pile"
    
    # Non-treasures should still be in hand
    hand_names = [card.name for card in player.hand]
    assert "Estate" in hand_names, "Estate should still be in hand"
    assert "Market" in hand_names, "Market should still be in hand"
    assert len(player.hand) == 2, "Should have 2 non-treasure cards left in hand"


def test_treasures_contribute_coins_when_moved():
    """Test that treasures add their coin value when moved to played"""
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Market", "Smithy", "Village", "Cellar", "Workshop",
                           "Chapel", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    player = game.current_player
    
    # Set up hand with specific treasures
    player.hand = [
        Card.create("Copper"),   # +1 coin
        Card.create("Silver"),   # +2 coins
        Card.create("Silver"),   # +2 coins
        Card.create("Gold"),     # +3 coins
    ]
    
    player.played = []
    player.coins = 0
    player.actions = 0
    
    # Transition to buy phase
    game.check_for_end_of_phase()
    
    # Check coins were added correctly
    assert player.coins == 8, f"Should have 8 coins (1+2+2+3), but has {player.coins}"
    assert game.phase == Phase.BUY


def test_no_treasures_in_hand():
    """Test transition when no treasures in hand"""
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Market", "Smithy", "Village", "Cellar", "Workshop",
                           "Chapel", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    player = game.current_player
    
    # Hand with no treasures
    player.hand = [
        Card.create("Estate"),
        Card.create("Market"),
        Card.create("Village")
    ]
    
    player.played = []
    player.coins = 0
    player.actions = 0
    
    initial_hand_size = len(player.hand)
    
    # Transition to buy phase
    game.check_for_end_of_phase()
    
    # No cards should move to played
    assert len(player.played) == 0, "No cards should be in played pile"
    assert len(player.hand) == initial_hand_size, "Hand size should not change"
    assert player.coins == 0, "Should have 0 coins"
    assert game.phase == Phase.BUY, "Should still transition to buy phase"


def test_treasures_not_moved_if_actions_remain():
    """Test that treasures are NOT moved if player still has actions"""
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Market", "Smithy", "Village", "Cellar", "Workshop",
                           "Chapel", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    player = game.current_player
    
    # Setup hand with treasures and action cards
    player.hand = [
        Card.create("Copper"),
        Card.create("Silver"),
        Card.create("Market"),  # Action card
    ]
    
    player.played = []
    player.actions = 1  # Still has actions!
    
    # Check phase transition
    game.check_for_end_of_phase()
    
    # Should still be in action phase
    assert game.phase == Phase.ACTION, "Should still be in action phase"
    
    # Treasures should NOT be moved
    assert len(player.played) == 0, "No cards should be moved to played yet"
    assert len(player.hand) == 3, "All cards should still be in hand"


def test_only_treasures_moved_not_other_cards():
    """Test that ONLY treasure cards are moved, not victory or action cards"""
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Market", "Smithy", "Village", "Cellar", "Workshop",
                           "Chapel", "Militia", "Remodel", "Mine", "Moat"]
    )
    game.controller = MockController(game)
    
    player = game.current_player
    
    # Mixed hand
    player.hand = [
        Card.create("Copper"),
        Card.create("Estate"),
        Card.create("Silver"),
        Card.create("Duchy"),
        Card.create("Market"),
        Card.create("Gold"),
        Card.create("Province"),
    ]
    
    player.played = []
    player.actions = 0
    
    # Transition
    game.check_for_end_of_phase()
    
    # Only treasures in played
    assert len(player.played) == 3, "Should have exactly 3 treasures in played"
    for card in player.played:
        assert isinstance(card, TreasureCard), f"{card.name} in played pile should be a TreasureCard"
    
    # Others still in hand
    assert len(player.hand) == 4, "Should have 4 non-treasure cards in hand"
    for card in player.hand:
        assert not isinstance(card, TreasureCard), f"{card.name} in hand should NOT be a TreasureCard"