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

def test_laboratory_is_action_card():
    """Test that Laboratory is an ActionCard"""
    from dominion.card import Card, ActionCard
    
    card_type = Card.get_type_with_name("Laboratory")
    assert issubclass(card_type, ActionCard), \
        "Laboratory should be an ActionCard"

def test_laboratory_effect():
    """Test Laboratory gives +2 Cards, +1 Action"""
    from dominion.game import DominionGame
    from dominion.card import Card
    from dominion.controller import Controller
    
    # Create a minimal test game
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Laboratory", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    # Mock controller
    class MockController(Controller):
        def __init__(self, game):
            self.game = game
            
        @property
        def current_player(self):
            """Some cards might access controller.current_player directly"""
            return self.game.current_player
            
        def trash(self, card):
            self.game.trash.append(card)
            
        def ask_yes_no(self, prompt):
            return False
            
        def pick_card_from_supply(self, player=None, maximum_cost=None):
            return None
            
        def pick_action(self, cards):
            return None
            
        def pick_cards_from_list(self, cards, minimum=0, maximum=None):
            return []
            
        def pick_cards_from_hand(self, player, minimum=0, maximum=None):
            return []
            
        def pick_card_from_hand(self, player):
            return None
            
        def pick_card_from_list(self, cards):
            return cards[0] if cards else None
            
        def pick_cards_from_discard_pile(self, player, maximum=1):
            return []
            
        def pick_cards(self, cards, minimum=0, maximum=None):
            return ([], cards)  # Return (selected, remaining)
            
        def pick_card_from_supply(self, maximum_cost=None):
            return None
    
    controller = MockController(game)
    game.controller = controller
    
    player = game.current_player
    
    # Give player a Laboratory card
    lab_card = Card.create("Laboratory")
    player.hand.append(lab_card)
    
    # Set up known state
    initial_hand_size = len(player.hand) - 1  # Minus the lab card
    initial_actions = player.actions
    initial_deck_discard_size = len(player.deck.cards) + len(player.discard_pile.cards)
    
    # Play Laboratory
    game.action(player, lab_card)
    
    # Check effects
    assert len(player.hand) == initial_hand_size + 2, \
        f"Laboratory should draw 2 cards, but hand went from {initial_hand_size} to {len(player.hand)}"
    
    assert player.actions == initial_actions, \
        f"Laboratory should give +1 action (net 0 after playing), but actions went from {initial_actions} to {player.actions}"
    
    # Verify cards were actually drawn from deck
    final_deck_discard_size = len(player.deck.cards) + len(player.discard_pile.cards)
    assert final_deck_discard_size == initial_deck_discard_size - 2, \
        "Laboratory should have drawn 2 cards from deck/discard"

def test_laboratory_with_empty_deck():
    """Test Laboratory when deck needs reshuffling"""
    from dominion.game import DominionGame
    from dominion.card import Card, Copper
    from dominion.controller import Controller
    
    # Create game
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Laboratory", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    # Mock controller
    class MockController(Controller):
        def __init__(self, game):
            self.game = game
            
        @property
        def current_player(self):
            """Some cards might access controller.current_player directly"""
            return self.game.current_player
            
        def trash(self, card):
            self.game.trash.append(card)
            
        def ask_yes_no(self, prompt):
            return False
            
        def pick_card_from_supply(self, player=None, maximum_cost=None):
            return None
            
        def pick_action(self, cards):
            return None
            
        def pick_cards_from_list(self, cards, minimum=0, maximum=None):
            return []
            
        def pick_cards_from_hand(self, player, minimum=0, maximum=None):
            return []
            
        def pick_card_from_hand(self, player):
            return None
            
        def pick_card_from_list(self, cards):
            return cards[0] if cards else None
            
        def pick_cards_from_discard_pile(self, player, maximum=1):
            return []
            
        def pick_cards(self, cards, minimum=0, maximum=None):
            return ([], cards)  # Return (selected, remaining)
            
        def pick_card_from_supply(self, maximum_cost=None):
            return None
    
    controller = MockController(game)
    game.controller = controller
    
    player = game.current_player
    
    # Setup: empty deck, cards in discard
    player.deck.cards = []  # Empty deck
    # Move most cards to discard
    while len(player.hand) > 1:
        card = player.hand.pop()
        player.discard_pile.add(card)
    
    # Add some coppers to discard to ensure we have cards to draw
    for _ in range(5):
        player.discard_pile.add(Card.create("Copper"))
    
    discard_size_before = len(player.discard_pile.cards)
    
    # Give player Laboratory
    lab_card = Card.create("Laboratory")
    player.hand.append(lab_card)
    
    # Play Laboratory - should trigger reshuffle
    game.action(player, lab_card)
    
    # Should have drawn 2 cards after reshuffling, plus the original card
    assert len(player.hand) == 3, \
        f"Should have 3 cards in hand after playing Laboratory (original card + 2 drawn), but have {len(player.hand)}"
    
    # Discard should be empty (reshuffled into deck)
    assert len(player.discard_pile.cards) == 0, \
        "Discard pile should be empty after reshuffle"

def test_laboratory_play_method_signature():
    """Test that Laboratory has correct play method signature"""
    from dominion.card import Card
    import inspect
    
    lab_type = Card.get_type_with_name("Laboratory")
    
    # Check play method exists
    assert hasattr(lab_type, 'play'), \
        "Laboratory should have a play method"
    
    # Check signature
    sig = inspect.signature(lab_type.play)
    params = list(sig.parameters.keys())
    
    assert len(params) == 2, \
        f"Laboratory.play should have 2 parameters, has {len(params)}"
    
    assert params[0] == 'self', \
        "First parameter should be 'self'"
    
    # Should accept either 'game' or 'controller' based on the codebase style
    assert params[1] in ['game', 'controller'], \
        f"Second parameter should be 'game' or 'controller', not '{params[1]}'"