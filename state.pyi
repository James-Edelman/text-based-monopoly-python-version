from better_iterator import better_iter
from cards import chance_class, community_chest_class
from game import display_property_class, display_property_list_class, player_action_class, player_is_broke_class, refresh_board_class, trade_screen_class
from online import online_config_class

players_playing: int
dev_mode: bool
house_total: int
hotel_total: int
start_time: float
game_version: float
player_turn: better_iter
player: dict
current_screen: str

sub_async_input_override: bool
input_override_logic: None

player_display: list[list[str]]
property_data: list[dict[str, int, bool]]
station_rent: list[int]
prop_from_pos: dict[int]

chance: chance_class
community_chest: community_chest_class

refresh_board: refresh_board_class
display_property: display_property_class
display_property_list: display_property_list_class
player_action: player_action_class
player_is_broke: player_is_broke_class
trade_screen: trade_screen_class

online_config: online_config_class