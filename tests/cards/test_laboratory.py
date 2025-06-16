"""
Hidden test for Laboratory card implementation
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

def test_laboratory_exists():
    """Test that Laboratory card is registered"""
    from dominion.card import Card
    
    assert Card.exists_with_name("Laboratory"), \
        "Laboratory card should be registered"
    
    card_type = Card.get_type_with_name("Laboratory")
    assert card_type.cost == 5, \
        f"Laboratory should cost 5, but costs {card_type.cost}"

def test_laboratory_effect():
    """Test Laboratory gives +2 Cards, +1 Action"""
    from dominion.game import DominionGame
    from dominion.card import Card
    from dominion.controller import Controller
    
    # Create a minimal test game
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Laboratory"] + ["Market"] * 9
    )
    
    # Mock controller
    class MockController(Controller):
        def __init__(self, game):
            self.game = game
            
        def trash(self, card):
            pass
            
        def ask_yes_no(self, prompt):
            return False
            
        def pick_card_from_supply(self, maximum_cost=None):
            return None
            
        # ... other required methods
    
    controller = MockController(game)
    game.controller = controller
    
    player = game.current_player
    
    # Give player a Laboratory card
    lab_card = Card.create("Laboratory")
    player.hand.append(lab_card)
    
    # Set up known state
    initial_hand_size = len(player.hand) - 1  # Minus the lab card
    initial_actions = player.actions
    
    # Play Laboratory
    game.action(player, lab_card)
    
    # Check effects
    assert len(player.hand) == initial_hand_size + 2, \
        f"Laboratory should draw 2 cards, but hand went from {initial_hand_size} to {len(player.hand)}"
    
    assert player.actions == initial_actions, \
        f"Laboratory should give +1 action (net 0 after playing), but actions went from {initial_actions} to {player.actions}"
