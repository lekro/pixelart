import re

DEFAULT_IGNORE_REGEX = ['sapling.*', 'wheat_stage.*', '.*grass.*', 
                        'water.*', 'redstone_dust.*', 'repeater.*',
                        'dragon_egg', 'cake.*', 'fern', '.*_stage_.*', 
                        'flower.*', 'shulker.*', 'door.*',
                        'enchanting.*', 'double_plant.*', '.*_layer_.*', 
                        'deadbush', 'vine', 'hopper.*', 'portal',
                        'anvil.*', 'daylight.*', 'comparator.*', 'trip.*', 
                        'farmland.*', 'grass_side', 'mycelium_side',
                        'podzol_side', 'leaves.*', 'reeds', '.*pane.*', 
                        '.*_stem.*', 'endframe_.*', 'mushroom_red',
                        'mushroom_brown', 'web', 'tnt_top', 'cactus.*', 
                        'lava.*', 'chorus_plant', '.*torch_.*', 'chorus_.*',
                         'pumpkin_top', 'pumpkin_bottom', 'lever', 'rail_.*', 
                         'jukebox_top', 'trapdoor', 'stone_slab_top',
                         'ladder', 'iron_bars', 'brewing_stand', 
                         'crafting_table_.*', 'bookshelf', 'glazed_terracotta_brown',
                         'redstone_lamp_on', 'furnace_front_on', 'quartz_ore', 
                         'cauldron.*', 'debug.*', 'glass', 'end_rod',
                         'structure_block.*', 'mycelium.*', 'grass.*', 'itemframe.*', 
                         'furnace_top',
                         'iron_trapdoor', '.*_podzol_.*', 'concrete_powder.*',
                         'sand', 'red_sand', 'gravel', 'dispenser_.*', 'dropper_.*',
                         'observer_.*', 'frosted_ice_.*', 'furnace.*', 
                         'glazed_terracotta_.*[abcfghjmqstuvxz]+.*',
                         'ice.*', 'melon_.*', 'pumpkin_.*', 'mushroom.*',
                         'piston_.*', 'beacon',
                         'quartz_block_(chiseled)?(lines)?(bottom)?(top)?.*',
                         'purpur_pillar.*', 'slime', 'tnt_.*', 'mob_spawner',
                         'jukebox_top', '.*_command_block.*',
                         'bed_.*']

class NameFilter:

    def __init__(self, regexes=DEFAULT_IGNORE_REGEX, 
                 formats=['.png'], 
                 regex_blacklist=True,
                 regexes_compiled=False,
                 format_blacklist=False):
        if regexes_compiled:
            self.regexes = regexes
        else:
            self.regexes = []
            for regex in regexes:
                self.regexes.append(re.compile(regex))
        self.regex_blacklist = regex_blacklist
        self.formats = formats
        self.format_blacklist = format_blacklist

    def filter_file(self, name, ext):
        if ext.lower() in self.formats:
            if self.format_blacklist:
                return False
        else:
            if not self.format_blacklist:
                return False
        for regex in self.regexes:
            if regex.match(name) is not None:
                # If we are blacklisting, it matched once,
                # so we return false. If we aren't black-
                # listing, it matched once, so we pass it
                return not self.regex_blacklist
        # If we are blacklisting, it failed all the matches
        # so we return true. If we're not, it failed all the
        # matches so we return false...
        return self.regex_blacklist

    def filter_list(self, l):
        # We expect the format of l being a list of tuples
        # (name, ext) just like the filter_file function.
        # We use *f to unpack the tuple.
        return [f for f in l if self.filter_file(*f)]


