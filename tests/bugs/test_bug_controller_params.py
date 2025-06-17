"""
Test for controller parameter bug in action cards.
This test should FAIL on the buggy code where some cards use 'game' and others use 'controller'.
It should PASS when all action cards consistently use 'controller' as the parameter.
"""
import sys
import os
import inspect
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

from dominion.card import Card, ActionCard


def test_all_action_cards_use_controller_parameter():
    """All action cards should have play(self, controller) not play(self, game)"""
    
    failed_cards = []
    cards_checked = 0
    
    # Check all registered cards
    for card_type in Card.registered():
        if issubclass(card_type, ActionCard):
            cards_checked += 1
            
            # Get the play method
            play_method = getattr(card_type, 'play', None)
            if not play_method:
                failed_cards.append((card_type.name, "No play method found"))
                continue
            
            # Get the signature
            sig = inspect.signature(play_method)
            params = list(sig.parameters.keys())
            
            # Should have exactly 2 parameters: self and controller
            if len(params) != 2:
                failed_cards.append((
                    card_type.name, 
                    f"Wrong number of parameters: {params}"
                ))
                continue
            
            # Second parameter should be 'controller', not 'game' or anything else
            if params[1] != 'controller':
                failed_cards.append((
                    card_type.name, 
                    f"Wrong parameter name: '{params[1]}' (should be 'controller')"
                ))
    
    # Make sure we actually checked some cards
    assert cards_checked > 0, "No action cards found to test"
    
    # Report failures
    if failed_cards:
        failure_message = "The following action cards have incorrect play() signatures:\n"
        for card_name, issue in failed_cards:
            failure_message += f"  - {card_name}: {issue}\n"
        failure_message += "\nAll action cards should have: play(self, controller)"
        failure_message += "\nHint: MarketCard and SmithyCard incorrectly use 'game' instead of 'controller'"
        assert False, failure_message


def test_specific_buggy_cards():
    """Test the specific cards that have the bug in the starter code"""
    
    # These are the cards that specifically have the bug
    buggy_cards = ['Market', 'Smithy']
    
    for card_name in buggy_cards:
        # Get the card class
        card_type = Card.get_type_with_name(card_name)
        assert issubclass(card_type, ActionCard), f"{card_name} should be an ActionCard"
        
        # Check the play method signature
        play_method = getattr(card_type, 'play', None)
        assert play_method is not None, f"{card_name} should have a play method"
        
        sig = inspect.signature(play_method)
        params = list(sig.parameters.keys())
        
        # Check parameter name
        assert len(params) == 2, f"{card_name}.play() should have exactly 2 parameters (self, controller)"
        assert params[0] == 'self', f"First parameter should be 'self'"
        assert params[1] == 'controller', f"{card_name}.play() should take 'controller' not '{params[1]}'"


def test_correctly_implemented_cards_as_examples():
    """Verify that some cards are correctly implemented to serve as examples"""
    
    # These cards should already be correct in the starter code
    correct_cards = ['Cellar', 'Chancellor', 'Harbinger', 'Merchant', 'Vassal', 
                    'Village', 'Woodcutter', 'Workshop']
    
    at_least_one_correct = False
    
    for card_name in correct_cards:
        try:
            card_type = Card.get_type_with_name(card_name)
            if not issubclass(card_type, ActionCard):
                continue
                
            play_method = getattr(card_type, 'play', None)
            if not play_method:
                continue
                
            sig = inspect.signature(play_method)
            params = list(sig.parameters.keys())
            
            if len(params) == 2 and params[1] == 'controller':
                at_least_one_correct = True
                break
        except:
            continue
    
    assert at_least_one_correct, "There should be at least one correctly implemented card as an example"