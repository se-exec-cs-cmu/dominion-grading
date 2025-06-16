"""
Hidden test for estate supply bug
Students should NOT see this test!
"""
import sys
import os
sys.path.insert(0, os.environ.get('PYTHONPATH', '.'))

def test_estate_cards_not_from_supply():
    """Test that Estate cards are created, not drawn from supply"""
    from dominion.game import DominionGame
    from dominion.card import Estate
    
    # Track calls to supply.draw
    draw_calls = []
    original_draw = DominionGame.create.__wrapped__ if hasattr(DominionGame.create, '__wrapped__') else DominionGame.create
    
    def track_supply_draws(game):
        original_supply_draw = game.supply.draw
        def tracked_draw(card_name):
            draw_calls.append(card_name)
            return original_supply_draw(card_name)
        game.supply.draw = tracked_draw
        return game
    
    # Create game
    game = DominionGame.create(
        player_names=["Alice", "Bob"],
        kingdom_card_names=[
            "Market", "Smithy", "Village", "Cellar", "Workshop",
            "Militia", "Remodel", "Mine", "Library", "Moat"
        ]
    )
    
    # Hook into supply to track draws
    track_supply_draws(game)
    
    # Estate should NOT have been drawn from supply
    estate_draws = [c for c in draw_calls if c == "Estate"]
    assert len(estate_draws) == 0, \
        f"Estate cards should not be drawn from supply, but {len(estate_draws)} were drawn"
    
    # Supply should still have all Estates
    assert game.supply.remaining("Estate") == 24, \
        f"Supply should have 24 estates, but has {game.supply.remaining('Estate')}"
    
    # Each player should still have 3 estates
    for player in game.players:
        estates = [c for c in player.all_cards() if isinstance(c, Estate)]
        assert len(estates) == 3, \
            f"Player {player.name} should have 3 estates, but has {len(estates)}"
    
    # Copper should have been properly drawn (7 per player)
    assert game.supply.remaining("Copper") == 46, \
        f"Supply should have 46 copper (60 - 14), but has {game.supply.remaining('Copper')}"
