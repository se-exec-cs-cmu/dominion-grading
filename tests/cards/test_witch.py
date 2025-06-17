"""
Hidden test for Witch card implementation
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

def test_witch_exists():
    """Test that Witch card is registered"""
    from dominion.card import Card
    
    assert Card.exists_with_name("Witch"), \
        "Witch card should be registered"
    
    card_type = Card.get_type_with_name("Witch")
    assert card_type.cost == 5, \
        f"Witch should cost 5, but costs {card_type.cost}"

def test_witch_is_action_card():
    """Test that Witch is an ActionCard"""
    from dominion.card import Card, ActionCard
    
    card_type = Card.get_type_with_name("Witch")
    assert issubclass(card_type, ActionCard), \
        "Witch should be an ActionCard"

def test_witch_draw_effect():
    """Test that Witch draws 2 cards for the player"""
    from dominion.game import DominionGame
    from dominion.card import Card
    from dominion.controller import Controller
    
    # Create a test game
    game = DominionGame.create(
        player_names=["Alice", "Bob", "Charlie"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    # Mock controller
    class MockController(Controller):
        """Mock controller that implements all required abstract methods"""
        def __init__(self, game):
            self.game = game
            
        @property
        def current_player(self):
            """Some cards might access controller.current_player directly"""
            return self.game.current_player
            
        def trash(self, card):
            """Implementation of abstract method"""
            self.game.trash.append(card)
            
        def ask_yes_no(self, prompt):
            """Implementation of abstract method"""
            return False
            
        def pick_card_from_supply(self, maximum_cost=None):
            """Implementation of abstract method"""
            return None
            
        def pick_action(self, cards):
            """Implementation of abstract method"""
            return None
            
        def pick_cards_from_list(self, cards, minimum=0, maximum=None):
            """Implementation of abstract method"""
            return []
            
        def pick_cards_from_hand(self, player, minimum=0, maximum=None):
            """Implementation of abstract method"""
            return []
    
    controller = MockController(game)
    game.controller = controller
    
    player = game.current_player
    
    # Give player a Witch card
    witch_card = Card.create("Witch")
    player.hand.append(witch_card)
    
    # Note initial hand size
    initial_hand_size = len(player.hand) - 1  # Minus the witch card
    initial_deck_discard = len(player.deck.cards) + len(player.discard_pile.cards)
    
    # Play Witch
    game.action(player, witch_card)
    
    # Check that player drew 2 cards
    assert len(player.hand) == initial_hand_size + 2, \
        f"Witch should draw 2 cards, but hand went from {initial_hand_size} to {len(player.hand)}"
    
    # Verify cards came from deck/discard
    final_deck_discard = len(player.deck.cards) + len(player.discard_pile.cards)
    assert final_deck_discard == initial_deck_discard - 2, \
        "Witch should have drawn 2 cards from deck/discard"

def test_witch_curse_distribution():
    """Test that Witch gives each other player a Curse"""
    from dominion.game import DominionGame
    from dominion.card import Card, CurseCard
    from dominion.controller import Controller
    
    # Create a test game with 3 players
    game = DominionGame.create(
        player_names=["Alice", "Bob", "Charlie"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    # Mock controller
    class MockController(Controller):
        """Mock controller that implements all required abstract methods"""
        def __init__(self, game):
            self.game = game
            
        @property
        def current_player(self):
            """Some cards might access controller.current_player directly"""
            return self.game.current_player
            
        def trash(self, card):
            """Implementation of abstract method"""
            self.game.trash.append(card)
            
        def ask_yes_no(self, prompt):
            """Implementation of abstract method"""
            return False
            
        def pick_card_from_supply(self, maximum_cost=None):
            """Implementation of abstract method"""
            return None
            
        def pick_action(self, cards):
            """Implementation of abstract method"""
            return None
            
        def pick_cards_from_list(self, cards, minimum=0, maximum=None):
            """Implementation of abstract method"""
            return []
            
        def pick_cards_from_hand(self, player, minimum=0, maximum=None):
            """Implementation of abstract method"""
            return []
            
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
    
    controller = MockController(game)
    game.controller = controller
    
    alice = game.current_player  # First player
    bob = game.players[1]
    charlie = game.players[2]
    
    # Count initial curses for each player
    def count_curses(player):
        return sum(1 for card in player.all_cards() if isinstance(card, CurseCard))
    
    bob_initial_curses = count_curses(bob)
    charlie_initial_curses = count_curses(charlie)
    alice_initial_curses = count_curses(alice)
    
    # Note supply curse count
    initial_curse_supply = game.supply.remaining("Curse")
    
    # Give Alice a Witch and play it
    witch_card = Card.create("Witch")
    alice.hand.append(witch_card)
    game.action(alice, witch_card)
    
    # Check that Bob and Charlie each got a Curse
    assert count_curses(bob) == bob_initial_curses + 1, \
        f"Bob should have gained 1 Curse, but has {count_curses(bob) - bob_initial_curses}"
    assert count_curses(charlie) == charlie_initial_curses + 1, \
        f"Charlie should have gained 1 Curse, but has {count_curses(charlie) - charlie_initial_curses}"
    
    # Alice should not have gained a Curse
    assert count_curses(alice) == alice_initial_curses, \
        f"Alice (the player) should not gain a Curse"
    
    # Supply should have 2 fewer Curses
    assert game.supply.remaining("Curse") == initial_curse_supply - 2, \
        f"Supply should have 2 fewer Curses, but went from {initial_curse_supply} to {game.supply.remaining('Curse')}"

def test_witch_curse_goes_to_discard():
    """Test that Curses go to other players' discard piles"""
    from dominion.game import DominionGame
    from dominion.card import Card, CurseCard
    from dominion.controller import Controller
    
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    class MockController(Controller):
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
    
    controller = MockController(game)
    game.controller = controller
    
    alice = game.current_player
    bob = game.players[1]
    
    # Clear Bob's discard pile to make it easier to check
    bob.discard_pile.cards = []
    
    # Play Witch
    witch_card = Card.create("Witch")
    alice.hand.append(witch_card)
    game.action(alice, witch_card)
    
    # Check that Bob's discard pile has a Curse
    assert len(bob.discard_pile.cards) == 1, \
        "Bob should have exactly 1 card in discard pile"
    assert isinstance(bob.discard_pile.cards[0], CurseCard), \
        "The card in Bob's discard pile should be a Curse"

def test_witch_empty_curse_pile():
    """Test Witch behavior when Curse pile is empty"""
    from dominion.game import DominionGame
    from dominion.card import Card, CurseCard
    from dominion.controller import Controller
    
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    class MockController(Controller):
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
    
    controller = MockController(game)
    game.controller = controller
    
    alice = game.current_player
    bob = game.players[1]
    
    # Empty the Curse supply
    game.supply._card_name_to_remaining["Curse"] = 0
    
    # Count Bob's cards before
    bob_cards_before = len(bob.all_cards())
    alice_hand_before = len(alice.hand)
    
    # Play Witch
    witch_card = Card.create("Witch")
    alice.hand.append(witch_card)
    
    # This should not crash even with no Curses available
    game.action(alice, witch_card)
    
    # Bob should not have gained any cards
    assert len(bob.all_cards()) == bob_cards_before, \
        "Bob should not gain cards when Curse pile is empty"
    
    # Alice should still draw 2 cards
    assert len(alice.hand) == alice_hand_before + 2, \
        "Alice should still draw 2 cards even when Curse pile is empty"

def test_witch_with_four_players():
    """Test Witch affects all other players in 4-player game"""
    from dominion.game import DominionGame
    from dominion.card import Card, CurseCard
    from dominion.controller import Controller
    
    game = DominionGame.create(
        player_names=["Alice", "Bob", "Charlie", "Diana"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    class MockController(Controller):
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
    
    controller = MockController(game)
    game.controller = controller
    
    alice = game.current_player
    
    # Count initial curses
    def count_curses(player):
        return sum(1 for card in player.all_cards() if isinstance(card, CurseCard))
    
    other_players = [p for p in game.players if p != alice]
    initial_curses = {p.name: count_curses(p) for p in other_players}
    
    # Play Witch
    witch_card = Card.create("Witch")
    alice.hand.append(witch_card)
    game.action(alice, witch_card)
    
    # Each other player should have gained exactly 1 Curse
    for player in other_players:
        new_curse_count = count_curses(player)
        assert new_curse_count == initial_curses[player.name] + 1, \
            f"{player.name} should have gained exactly 1 Curse"

def test_witch_play_method_signature():
    """Test that Witch has correct play method signature"""
    from dominion.card import Card
    import inspect
    
    witch_type = Card.get_type_with_name("Witch")
    
    # Check play method exists
    assert hasattr(witch_type, 'play'), \
        "Witch should have a play method"
    
    # Check signature
    sig = inspect.signature(witch_type.play)
    params = list(sig.parameters.keys())
    
    assert len(params) == 2, \
        f"Witch.play should have 2 parameters, has {len(params)}"
    
    assert params[0] == 'self', \
        "First parameter should be 'self'"
    
    # Should accept either 'game' or 'controller' based on the codebase style
    assert params[1] in ['game', 'controller'], \
        f"Second parameter should be 'game' or 'controller', not '{params[1]}'"

def test_witch_partial_curse_distribution():
    """Test Witch with only 1 Curse left in supply for 3 players"""
    from dominion.game import DominionGame
    from dominion.card import Card, CurseCard
    from dominion.controller import Controller
    
    game = DominionGame.create(
        player_names=["Alice", "Bob", "Charlie"],
        kingdom_card_names=["Witch", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    class MockController(Controller):
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
    
    controller = MockController(game)
    game.controller = controller
    
    alice = game.current_player
    bob = game.players[1]
    charlie = game.players[2]
    
    # Set Curse supply to 1
    game.supply._card_name_to_remaining["Curse"] = 1
    
    # Count initial curses
    def count_curses(player):
        return sum(1 for card in player.all_cards() if isinstance(card, CurseCard))
    
    bob_initial = count_curses(bob)
    charlie_initial = count_curses(charlie)
    
    # Play Witch
    witch_card = Card.create("Witch")
    alice.hand.append(witch_card)
    game.action(alice, witch_card)
    
    # Exactly one of Bob or Charlie should get a Curse
    bob_gained = count_curses(bob) - bob_initial
    charlie_gained = count_curses(charlie) - charlie_initial
    
    assert bob_gained + charlie_gained == 1, \
        "Exactly 1 Curse should have been distributed when only 1 was available"
    
    # Supply should be empty
    assert game.supply.remaining("Curse") == 0, \
        "Curse pile should be empty"