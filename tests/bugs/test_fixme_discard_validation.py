"""
Test for FIXME: player.py line 37 - discard() should validate card is in hand
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

import pytest
from dominion.player import Player
from dominion.card import Card


def test_discard_card_not_in_hand_raises_error():
    """Test that discarding a card not in hand raises an appropriate error"""
    player = Player("TestPlayer")
    
    # Give player some cards
    copper1 = Card.create("Copper")
    copper2 = Card.create("Copper")
    estate = Card.create("Estate")
    
    player.hand = [copper1, estate]
    
    # Try to discard a card that's not in hand
    with pytest.raises((ValueError, AssertionError)) as exc_info:
        player.discard(copper2)  # copper2 is not in hand
    
    # The error message should be informative
    error_msg = str(exc_info.value).lower()
    assert "hand" in error_msg or "not in" in error_msg or "cannot discard" in error_msg, \
        f"Error message should indicate card is not in hand, but was: {exc_info.value}"


def test_discard_none_raises_error():
    """Test that discarding None raises an appropriate error"""
    player = Player("TestPlayer")
    player.hand = [Card.create("Copper")]
    
    with pytest.raises((ValueError, AssertionError, TypeError)):
        player.discard(None)


def test_discard_valid_card_works():
    """Test that discarding a card that IS in hand still works correctly"""
    player = Player("TestPlayer")
    
    copper = Card.create("Copper")
    estate = Card.create("Estate")
    player.hand = [copper, estate]
    
    # This should work fine
    player.discard(copper)
    
    # Verify the card was moved correctly
    assert copper not in player.hand, "Card should be removed from hand"
    assert copper in player.discard_pile.cards, "Card should be in discard pile"
    assert len(player.hand) == 1, "Hand should have one card left"
    assert estate in player.hand, "Estate should still be in hand"


def test_discard_same_card_type_different_instance():
    """Test discarding when hand has same card type but different instance"""
    player = Player("TestPlayer")
    
    # Create two different Copper instances
    copper_in_hand = Card.create("Copper")
    copper_not_in_hand = Card.create("Copper")
    
    player.hand = [copper_in_hand]
    
    # Should fail - even though both are Coppers, they're different instances
    with pytest.raises((ValueError, AssertionError)):
        player.discard(copper_not_in_hand)
    
    # But discarding the actual instance should work
    player.discard(copper_in_hand)
    assert len(player.hand) == 0
    assert copper_in_hand in player.discard_pile.cards


def test_discard_from_empty_hand():
    """Test discarding from empty hand raises error"""
    player = Player("TestPlayer")
    player.hand = []
    
    copper = Card.create("Copper")
    
    with pytest.raises((ValueError, AssertionError)):
        player.discard(copper)