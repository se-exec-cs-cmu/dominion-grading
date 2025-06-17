"""
Hidden test for Gardens card implementation
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))


def test_gardens_exists():
    """Test that Laboratory card is registered"""
    from dominion.card import Card
    
    assert Card.exists_with_name("Gardens"), \
        "Gardens card should be registered"
    
    card_type = Card.get_type_with_name("Gardens")
    assert card_type.cost == 4, \
        f"Laboratory should cost 4, but costs {card_type.cost}"

def test_gardens_is_victory_card():
    """Test that Gardens is a VictoryCard (not an ActionCard)"""
    from dominion.card import Card, VictoryCard, ActionCard, ScoringCard
    
    card_type = Card.get_type_with_name("Gardens")
    assert issubclass(card_type, VictoryCard), \
        "Gardens should be a VictoryCard"
    assert issubclass(card_type, ScoringCard), \
        "Gardens should be a ScoringCard"
    assert not issubclass(card_type, ActionCard), \
        "Gardens should NOT be an ActionCard"

def test_gardens_scoring_basic():
    """Test Gardens scoring: 1 VP per 10 cards (rounded down)"""
    from dominion.game import DominionGame
    from dominion.card import Card
    from dominion.player import Player
    
    # Create a simple player for testing
    player = Player("TestPlayer")
    
    # Create a Gardens card
    gardens = Card.create("Gardens")
    
    # Test various card counts
    test_cases = [
        (0, 0),    # 0 cards = 0 VP
        (1, 0),    # 1 card = 0 VP
        (9, 0),    # 9 cards = 0 VP
        (10, 1),   # 10 cards = 1 VP
        (11, 1),   # 11 cards = 1 VP
        (19, 1),   # 19 cards = 1 VP
        (20, 2),   # 20 cards = 2 VP
        (25, 2),   # 25 cards = 2 VP
        (30, 3),   # 30 cards = 3 VP
        (39, 3),   # 39 cards = 3 VP
        (40, 4),   # 40 cards = 4 VP
        (50, 5),   # 50 cards = 5 VP
        (99, 9),   # 99 cards = 9 VP
        (100, 10), # 100 cards = 10 VP
    ]
    
    for total_cards, expected_vp in test_cases:
        # Clear player's cards
        player.hand = []
        player.deck.cards = []
        player.discard_pile.cards = []
        player.played = []
        
        # Add the specified number of cards (using Copper as dummy cards)
        for _ in range(total_cards):
            player.deck.cards.append(Card.create("Copper"))
        
        # Calculate score from Gardens
        score = gardens.score(player)
        
        assert score == expected_vp, \
            f"With {total_cards} cards, Gardens should give {expected_vp} VP, but gave {score} VP"

def test_gardens_counts_all_card_locations():
    """Test that Gardens counts cards in all locations (hand, deck, discard, played)"""
    from dominion.game import DominionGame
    from dominion.card import Card
    from dominion.player import Player
    
    player = Player("TestPlayer")
    gardens = Card.create("Gardens")
    
    # Start with empty player
    player.hand = []
    player.deck.cards = []
    player.discard_pile.cards = []
    player.played = []
    
    # Add 3 cards to each location (total 12 = 1 VP)
    for _ in range(3):
        player.hand.append(Card.create("Copper"))
        player.deck.cards.append(Card.create("Silver"))
        player.discard_pile.cards.append(Card.create("Gold"))
        player.played.append(Card.create("Estate"))
    
    # Total should be 12 cards = 1 VP
    score = gardens.score(player)
    assert score == 1, \
        f"With 12 cards spread across locations, Gardens should give 1 VP, but gave {score} VP"
    
    # Verify it's actually counting all locations
    assert len(player.all_cards()) == 12, \
        "Player should have 12 total cards"

def test_gardens_in_game_scoring():
    """Test Gardens scoring in actual game context"""
    from dominion.game import DominionGame
    from dominion.card import Card
    
    # Create a game with Gardens
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=["Gardens", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    player = game.players[0]
    
    # Give player some Gardens cards
    player.discard_pile.add(Card.create("Gardens"))
    player.discard_pile.add(Card.create("Gardens"))
    
    # Player starts with 10 cards (7 Copper + 3 Estate)
    # So each Gardens is worth 1 VP
    initial_score = player.score()  # 3 VP from Estates + 2 VP from Gardens = 5
    
    # Add 10 more cards to make total 20 cards
    for _ in range(10):
        player.discard_pile.add(Card.create("Copper"))
    
    # Now each Gardens is worth 2 VP
    new_score = player.score()  # 3 VP from Estates + 4 VP from Gardens = 7
    
    assert new_score == initial_score + 2, \
        f"Adding 10 cards should increase Gardens value by 2 VP total, but score went from {initial_score} to {new_score}"

def test_multiple_gardens():
    """Test that multiple Gardens cards score independently"""
    from dominion.card import Card
    from dominion.player import Player
    
    player = Player("TestPlayer")
    
    # Clear player's cards
    player.hand = []
    player.deck.cards = []
    player.discard_pile.cards = []
    player.played = []
    
    # Add 30 cards (3 VP per Gardens)
    for _ in range(30):
        player.deck.cards.append(Card.create("Copper"))
    
    # Add 3 Gardens cards
    gardens1 = Card.create("Gardens")
    gardens2 = Card.create("Gardens")
    gardens3 = Card.create("Gardens")
    
    # Each should give 3 VP
    assert gardens1.score(player) == 3, "First Gardens should give 3 VP"
    assert gardens2.score(player) == 3, "Second Gardens should give 3 VP"
    assert gardens3.score(player) == 3, "Third Gardens should give 3 VP"
    
    # Add all Gardens to player's cards
    player.deck.cards.extend([gardens1, gardens2, gardens3])
    
    # Now we have 33 cards total, still 3 VP each
    assert gardens1.score(player) == 3, "Gardens should still give 3 VP with 33 cards"
    
    # Total score from Gardens
    total_gardens_score = sum(card.score(player) for card in [gardens1, gardens2, gardens3])
    assert total_gardens_score == 9, f"Three Gardens with 33 cards should give 9 VP total, but gave {total_gardens_score}"

def test_gardens_not_action_card():
    """Ensure Gardens cannot be played as an action"""
    from dominion.game import DominionGame
    from dominion.card import Card, ActionCard
    
    game = DominionGame.create(
        player_names=["Alice"],
        kingdom_card_names=["Gardens", "Market", "Smithy", "Village", "Cellar", 
                           "Workshop", "Militia", "Remodel", "Mine", "Moat"]
    )
    
    player = game.current_player
    gardens = Card.create("Gardens")
    player.hand.append(gardens)
    
    # Gardens should not be in the list of playable action cards
    action_cards = [card for card in player.hand if isinstance(card, ActionCard)]
    assert gardens not in action_cards, \
        "Gardens should not be considered an action card"
    
    # Attempting to play Gardens as an action should fail
    # (This would raise an assertion error in the actual game)
    try:
        game.action(player, gardens)
        assert False, "Should not be able to play Gardens as an action"
    except (AssertionError, AttributeError):
        # Expected - Gardens doesn't have a play() method
        pass