"""
Test for FIXME: player.py line 43 - draw_into_hand() should handle n > available cards
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

from dominion.player import Player
from dominion.card import Card


def test_draw_more_than_available_cards():
    """Test drawing more cards than exist in deck + discard"""
    player = Player("TestPlayer")
    
    # Set up a small deck and discard pile
    player.deck.cards = [Card.create("Copper"), Card.create("Copper")]
    player.discard_pile.cards = [Card.create("Estate")]
    player.hand = []
    
    # Total available: 3 cards
    # Try to draw 5 cards
    drawn = player.draw_into_hand(5)
    
    # Should draw all 3 available cards
    assert len(drawn) == 3, f"Should draw 3 cards (all available), but drew {len(drawn)}"
    assert len(player.hand) == 3, f"Hand should have 3 cards, but has {len(player.hand)}"
    assert len(player.deck.cards) == 0, "Deck should be empty"
    assert len(player.discard_pile.cards) == 0, "Discard should be empty"


def test_draw_exactly_available_cards():
    """Test drawing exactly the number of available cards"""
    player = Player("TestPlayer")
    
    # 2 in deck, 3 in discard = 5 total
    player.deck.cards = [Card.create("Copper"), Card.create("Silver")]
    player.discard_pile.cards = [Card.create("Estate"), Card.create("Duchy"), Card.create("Gold")]
    player.hand = []
    
    drawn = player.draw_into_hand(5)
    
    assert len(drawn) == 5, "Should draw exactly 5 cards"
    assert len(player.hand) == 5, "Hand should have 5 cards"
    assert len(player.deck.cards) == 0, "Deck should be empty"
    assert len(player.discard_pile.cards) == 0, "Discard should be empty"


def test_draw_from_empty_deck_and_discard():
    """Test drawing when both deck and discard are empty"""
    player = Player("TestPlayer")
    
    # Empty deck and discard
    player.deck.cards = []
    player.discard_pile.cards = []
    player.hand = [Card.create("Copper")]  # One card in hand
    
    # Try to draw 3 cards
    drawn = player.draw_into_hand(3)
    
    # Should draw 0 cards
    assert len(drawn) == 0, "Should draw 0 cards when deck and discard are empty"
    assert len(player.hand) == 1, "Hand should still have just the original card"


def test_draw_triggers_reshuffle_correctly():
    """Test that drawing triggers reshuffle and continues correctly"""
    player = Player("TestPlayer")
    
    # 1 card in deck, 4 in discard
    player.deck.cards = [Card.create("Copper")]
    player.discard_pile.cards = [
        Card.create("Silver"),
        Card.create("Gold"),
        Card.create("Estate"),
        Card.create("Duchy")
    ]
    player.hand = []
    
    # Try to draw 3 cards
    drawn = player.draw_into_hand(3)
    
    # Should draw 3 cards (1 from deck, then reshuffle, then 2 more)
    assert len(drawn) == 3, "Should draw 3 cards with reshuffle"
    assert len(player.hand) == 3, "Hand should have 3 cards"
    # After drawing 3, should have 2 left in deck
    assert len(player.deck.cards) == 2, f"Should have 2 cards left in deck, but has {len(player.deck.cards)}"
    assert len(player.discard_pile.cards) == 0, "Discard should be empty after reshuffle"


def test_draw_very_large_number():
    """Test drawing an unreasonably large number of cards"""
    player = Player("TestPlayer")
    
    # Just 5 cards total
    player.deck.cards = [Card.create("Copper") for _ in range(3)]
    player.discard_pile.cards = [Card.create("Estate") for _ in range(2)]
    player.hand = []
    
    # Try to draw 1000 cards
    drawn = player.draw_into_hand(1000)
    
    # Should only draw the 5 available
    assert len(drawn) == 5, "Should only draw the 5 available cards"
    assert len(player.hand) == 5, "Hand should have 5 cards"
    assert len(player.deck.cards) == 0, "Deck should be empty"
    assert len(player.discard_pile.cards) == 0, "Discard should be empty"


def test_draw_returns_correct_cards():
    """Test that draw_into_hand returns the actual cards drawn"""
    player = Player("TestPlayer")
    
    # Create specific cards to track
    copper = Card.create("Copper")
    silver = Card.create("Silver")
    gold = Card.create("Gold")
    
    player.deck.cards = [copper, silver, gold]
    player.discard_pile.cards = []
    player.hand = []
    
    # Draw 2 cards
    drawn = player.draw_into_hand(2)
    
    # Should return the cards that were drawn
    assert len(drawn) == 2, "Should return 2 cards"
    assert copper in drawn, "Copper should be in drawn cards"
    assert silver in drawn, "Silver should be in drawn cards"
    assert gold not in drawn, "Gold should not be in drawn cards"
    
    # And they should be in hand
    assert copper in player.hand, "Copper should be in hand"
    assert silver in player.hand, "Silver should be in hand"