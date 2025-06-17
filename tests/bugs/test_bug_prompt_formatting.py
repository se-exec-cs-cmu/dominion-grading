"""
Test for prompt formatting bug in controller.pick_cards_from_list.
This test should FAIL on the buggy code where string formatting uses {variable} without f-string.
It should PASS when the prompts are properly formatted as f-strings.
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

from dominion.controller import CliController
from dominion.card import Card, Copper, Silver, Gold
from unittest.mock import Mock, MagicMock


def test_pick_cards_prompt_formatting():
    """Test that prompts in pick_cards_from_list show actual numbers, not {placeholders}"""
    
    # Create mock CLI that captures output
    mock_cli = Mock()
    captured_prompts = []
    
    def capture_bold(text):
        captured_prompts.append(text)
        return text
    
    mock_cli.bold = capture_bold
    mock_cli.ask.return_value = "0"  # Always select first card
    
    # Create a mock game to avoid initialization issues
    mock_game = MagicMock()
    mock_game.current_player = MagicMock()
    
    # Create controller with mocked CLI and game
    controller = CliController(cli=mock_cli, game=mock_game)
    
    # Test cards for picking
    test_cards = [Copper(), Silver(), Gold()]
    
    # Test cases with different min/max combinations
    test_cases = [
        (2, 2, "exactly 2"),      # minimum == maximum
        (1, 3, "between 1 and 3"), # minimum < maximum
        (0, 2, "at most 2"),      # minimum == 0, maximum set
        (0, None, "any number"),   # minimum == 0, no maximum
        (1, None, "at least 1"),   # minimum > 0, no maximum
    ]
    
    for minimum, maximum, expected_phrase in test_cases:
        captured_prompts.clear()
        mock_cli.ask.return_value = "0"  # Reset response
        
        # Call the method
        try:
            controller.pick_cards_from_list(
                test_cards,
                minimum=minimum,
                maximum=maximum
            )
        except (ValueError, IndexError):
            # May fail on input validation, but we're testing the prompt
            pass
        
        # Check that a prompt was captured
        assert len(captured_prompts) > 0, f"No prompt was shown for min={minimum}, max={maximum}"
        
        prompt = captured_prompts[0]
        
        # The bug: prompt contains literal {minimum} or {maximum} instead of numbers
        assert "{minimum}" not in prompt, \
            f"Prompt contains unformatted {{minimum}} placeholder: '{prompt}'\n" \
            f"The string should be an f-string (e.g., f\"Pick exactly {{minimum}} cards\")"
        
        assert "{maximum}" not in prompt, \
            f"Prompt contains unformatted {{maximum}} placeholder: '{prompt}'\n" \
            f"The string should be an f-string (e.g., f\"Pick between {{minimum}} and {{maximum}} cards\")"
        
        # For debugging - show what prompt was actually generated
        print(f"Test case min={minimum}, max={maximum}: '{prompt}'")


def test_exact_number_case():
    """Test the specific case where minimum equals maximum"""
    
    mock_cli = Mock()
    captured_prompt = None
    
    def capture_bold(text):
        nonlocal captured_prompt
        captured_prompt = text
        return text
    
    mock_cli.bold = capture_bold
    mock_cli.ask.return_value = "0,1"  # Select exactly 2 cards
    
    mock_game = MagicMock()
    controller = CliController(cli=mock_cli, game=mock_game)
    
    cards = [Copper(), Silver(), Gold()]
    
    # Test minimum == maximum == 2
    try:
        controller.pick_cards_from_list(cards, minimum=2, maximum=2)
    except:
        pass
    
    assert captured_prompt is not None, "No prompt was captured"
    
    # Check for the bug
    assert "{minimum}" not in captured_prompt, \
        f"Bug found: prompt shows '{{minimum}}' instead of '2': {captured_prompt}"
    
    # The prompt should say "exactly 2" somewhere
    assert "2" in captured_prompt or "two" in captured_prompt.lower(), \
        f"The number 2 should appear in the prompt: {captured_prompt}"


def test_range_case():
    """Test the case where there's a range (minimum < maximum)"""
    
    mock_cli = Mock()
    captured_prompt = None
    
    def capture_bold(text):
        nonlocal captured_prompt
        captured_prompt = text
        return text
    
    mock_cli.bold = capture_bold
    mock_cli.ask.return_value = "0,1"
    
    mock_game = MagicMock()
    controller = CliController(cli=mock_cli, game=mock_game)
    
    cards = [Copper(), Silver(), Gold()]
    
    # Test range: minimum=1, maximum=3
    try:
        controller.pick_cards_from_list(cards, minimum=1, maximum=3)
    except:
        pass
    
    assert captured_prompt is not None, "No prompt was captured"
    
    # Check for the bug
    assert "{minimum}" not in captured_prompt and "{maximum}" not in captured_prompt, \
        f"Bug found: prompt contains placeholders: {captured_prompt}"
    
    # Should mention both numbers
    assert "1" in captured_prompt and "3" in captured_prompt, \
        f"The numbers 1 and 3 should appear in the prompt: {captured_prompt}"


def test_formatting_bug_line_location():
    """Test that helps identify the specific buggy lines in controller.py"""
    
    # This test inspects the actual source code if accessible
    try:
        from dominion import controller
        import inspect
        
        source = inspect.getsource(controller.CliController.pick_cards_from_list)
        
        # Look for prompt assignments that might have the bug
        buggy_patterns = [
            '"Pick exactly {minimum}',
            '"Pick between {minimum} and {maximum}',
            '"Pick at most {maximum}',
            '"Pick at least {minimum}',
            "'Pick exactly {minimum}",
            "'Pick between {minimum} and {maximum}",
        ]
        
        found_bugs = []
        for pattern in buggy_patterns:
            if pattern in source:
                found_bugs.append(pattern)
        
        if found_bugs:
            msg = "Found string formatting bugs in pick_cards_from_list:\n"
            for bug in found_bugs:
                msg += f"  - {bug} should be f{bug}\n"
            msg += "\nHint: Add 'f' prefix to make them f-strings"
            assert False, msg
            
    except Exception:
        # If we can't inspect the source, skip this check
        pass