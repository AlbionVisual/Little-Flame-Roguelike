import arcade
from game_map_generator import GameMapGenerator
from map import map_types_relation
from sprites import *

class GamePlayerController(GameMapGenerator):
    def change_lights(self, new_lights):
        for i in range(2):
            for cell in self.lighten[i] - new_lights[i]:
                if not cell.is_visible: cell.set_tile( self.tile_textures[map_types_relation[i+1]] )
                cell.change_texture(light = False)
                self.map.chunks[(cell.center_x // self.settings['TILE_SIZE'] // 16, cell.center_y // self.settings['TILE_SIZE'] // 16)].field[cell.center_y // self.settings['TILE_SIZE'] % 16][cell.center_x // self.settings['TILE_SIZE'] % 16][0] -= 4
            for cell in new_lights[i] - self.lighten[i]:
                if not cell.is_visible: cell.set_tile( self.tile_textures[map_types_relation[i+1]] ) 
                cell.change_texture(light = True)
        
        for loot in self.scene["Loot"]:
            if map_types_relation[self.map.get(loot.chunk).field[loot.pos[1]][loot.pos[0]][0]] == 'lighten_floor':
                loot.change_texture(self.loot_textures[loot.type])
        
        for enemy in self.scene["Enemies"]:
            if map_types_relation[self.map.get(enemy.chunk).field[enemy.pos[1]][enemy.pos[0]][0]] == 'lighten_floor':
                enemy.visible = True


        self.lighten = new_lights

    def check_crafts(self):
        templates = [
            { # Sword
                'res': 7,
                'craft':[
                    ['#'],
                    ['#'],
                    ['$']
                ],
                'amount': 1,

            },
            { # Axe
                'res': 8,
                'craft':[
                    ['#', '#'],
                    ['$', '#'],
                    ['$', '*']
                ],
                'amount': 1
            },
            { # Apple 
                'res': 0,
                'craft':[
                    ['*', '$', '#', '*'],
                    ['#', '$', '#', '#'],
                    ['#', '#', '#', '#'],
                    ['*', '#', '#', '*']
                ],
                'amount': 12
            }
        ]

        min_x = int(self.player_sprite.center_x // self.settings['TILE_SIZE']) + 7
        max_x = int(self.player_sprite.center_x // self.settings['TILE_SIZE']) - 7
        min_y = int(self.player_sprite.center_y // self.settings['TILE_SIZE']) + 7
        max_y = int(self.player_sprite.center_y // self.settings['TILE_SIZE']) - 7
        field = [[None] * 14 for _ in range(14)]
        start_x, start_y = max_x, max_y

        def check_for_colision(craft, x, y):
            nonlocal field
            sym_types = {}
            min_amount = 0
            min_coords = ()
            for i, line in enumerate(reversed(craft)):
                if field[x - 1][y + i]: return False
                if field[x + len(craft[0])][y + i]: return False
                for j, patt in enumerate(line):
                    if field[x + j][y - 1]: return False
                    if field[x + j][y + len(craft)]: return False
                    if patt == '*': 
                        if field[x + j][y + i]: return False
                    else:
                        if not field[x + j][y + i]: return False
                        if patt in sym_types and field[x + j][y + i][0] != sym_types[patt]: return False
                        else: 
                            if field[x + j][y + i][0] in sym_types.values() and patt not in sym_types: return False
                            else:
                                sym_types[patt] = field[x + j][y + i][0]
                                if not min_amount:
                                    min_amount = field[x + j][y + i][1]
                                    min_coords = (x + j, y + i)
                                elif min_amount > field[x + j][y + i][1]:
                                    min_amount = field[x+j][y+i][1]
                                    min_coords = (x + j, y + i)
            return min_coords, min_amount

        def bring_back(pattern):
            nonlocal min_y, min_x, max_x, max_y, start_y, start_x
            for i in range(min_x, max_x - len(pattern[0]) + 1):
                for j in range(min_y, max_y - len(pattern) + 1):
                    res = check_for_colision(pattern, i - start_x, j - start_y)
                    if res: return (i, j, res[0][0] + start_x, res[0][1] + start_y, res[1])
            return False

        for coord, loot in self.active_loot.items():
            if coord[0] > max_x: max_x = coord[0]
            if coord[0] < min_x: min_x = coord[0]
            if coord[1] > max_y: max_y = coord[1]
            if coord[1] < min_y: min_y = coord[1]
            field[coord[0] - start_x][coord[1] - start_y] = [loot.type, loot.amount]
        
        max_x += 1
        max_y += 1

        for temp in templates:
            res = bring_back(temp['craft'])
            if res:
                for i in range(len(temp['craft'][0])):
                    for j in range(len(temp['craft'])):
                        cords = (res[0] + i, res[1] + j)
                        if cords in self.active_loot:
                            loot = self.active_loot[cords]
                            if loot.amount <= res[4]:
                                del self.active_loot[cords]
                                loot.remove_from_sprite_lists()
                                del self.map.get(loot.chunk).loot[loot.pos]
                            else: loot.amount -= res[4]
                
                amount = res[4]
                res = (res[2], res[3])
                x, y = (i // 16 for i in res)
                xi, yi = (i % 16 for i in res)
                chunk = self.map.get((x, y))
                loot = LootSprite(self.loot_textures[temp['res']], pickable=True)
                # loot.set_hit_box(self.settings['LOOT_HIT_BOX'])
                loot.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                loot.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                loot.pos = (xi, yi)
                loot.type = temp['res']
                loot.amount = temp['amount'] * amount
                loot.chunk = (x, y)
                chunk.loot[(xi, yi)] = {'type': temp['res'], 'sprite': loot}
                self.scene.add_sprite("Loot", loot)

                return
    
    def drop(self, all = False, coords = 'player'):
        slot = self.selector_sprite.slot
        if coords == 'player': coords = self.player_sprite.position
        posx, posy = (int(i // self.settings['TILE_SIZE']) for i in coords)
        chunk = self.map.get((posx // 16, posy // 16))
        if len(self.score) > slot and self.score[slot] > 0:
            if (posx % 16, posy % 16) not in chunk.loot:
                texture = self.loot_textures[self.labels[slot]['type']]
                loot = LootSprite(texture, pickable=False)
                # loot.set_hit_box(self.settings['LOOT_HIT_BOX'])

                loot.center_x = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posx
                loot.center_y = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posy
                loot.pos = (posx % 16, posy % 16)
                loot.type = self.labels[slot]['type']
                loot.chunk = tuple(chunk.pos)
                if all: loot.amount = self.score[slot]
                self.scene.add_sprite("Items", loot)
                chunk.loot[(posx % 16, posy % 16)] = {'type': self.labels[slot]['type'], 'pickable': False, 'sprite': loot}
                
                
                if all: self.score[slot] = 0
                else: self.score[slot] -= 1

                if self.score[slot] == 0:
                    del self.score[slot]
                    self.labels[slot]['sprite'].remove_from_sprite_lists()
                    del self.labels[slot]
                    for i in range(len(self.labels)):
                        self.labels[i]['sprite'].center_x = 20
                        self.labels[i]['sprite'].center_y = 40 * i + 20
                        self.labels[i]['label'].x = 32
                        self.labels[i]['label'].y = 40 * i + 4
                else:
                    self.labels[slot]['label'].text = str(self.score[slot])

            elif chunk.loot[(posx % 16, posy % 16)]['type'] == self.labels[slot]['type']:
                chunk.loot[(posx % 16, posy % 16)]['sprite'].amount += self.score[slot] if all else 1
                if not all: self.score[slot] -= 1
                else: self.score[slot] = 0

                if self.score[slot] == 0:
                    del self.score[slot]
                    self.labels[slot]['sprite'].remove_from_sprite_lists()
                    del self.labels[slot]
                    for i in range(len(self.labels)):
                        self.labels[i]['sprite'].center_x = 20
                        self.labels[i]['sprite'].center_y = 40 * i + 20
                        self.labels[i]['label'].x = 32
                        self.labels[i]['label'].y = 40 * i + 4
                else: self.labels[slot]['label'].text = str(self.score[slot])

    def pickup(self, scene = 'Loot', sprites = None):
        if sprites is None: sprites = []                            # Selecting sprites
        if scene:
            sprites += arcade.check_for_collision_with_list(
                self.player_sprite, self.scene[scene]
            )
        for loot in sprites:                                        # for every sprite in list

            self.player_sprite.health += self.settings["HEALTH_BOOST"] # Add health
            if self.player_sprite.health > 1.2: self.player_sprite.health = 1.2

            if loot.is_active:                                      # if active remove from active list
                cords = tuple(loot.pos[i] + val * 16 for i, val in enumerate(loot.chunk))
                del self.active_loot[cords]
                if len(self.active_loot) > 1: self.check_crafts()
                loot.is_active = False

            if scene: self.scene[scene].remove(loot)                # remove sprite from field
            if not loot.is_in_inventory(): del self.map.get(loot.chunk).loot[loot.pos]
            else: continue                                          # skip if dragged from inventory

            loot.remove_from_sprite_lists()
            for i, item in enumerate(self.labels):                  # if inventory has one += amount
                if item['type'] == loot.type:
                    self.score[i] += loot.amount
                    item['label'].text = str(self.score[i])
                    del loot
                    break
            else:                                                   # otherwise add new slot
                loot.center_x = 20
                loot.center_y = len(self.score) * 40 + 20
                loot.pos = None
                loot.chunk = None
                loot.pickable = False
                loot.scale = LootSprite.settings['LOOT_SCALING']
                self.interface.add_sprite("Icons",loot)
                self.score += [loot.amount]
                self.labels += [{'type': loot.type, 'label': arcade.Text(str(loot.amount), 32, (len(self.score) - 1) * 40 + 4, font_size=10), 'sprite': loot}]

    def enemy_collision(self):
        collided = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Enemies"]
        )
        for enemy in collided:
            if enemy.striking:
                self.player_sprite.health -= self.settings["ENEMY_HEAT_POINTS"]
                enemy.striking = False

    def atack(self):
        mouse_x = self.mouse_sprite.position[0] + self.camera.position[0] - self.window.width / 2
        mouse_y = self.mouse_sprite.position[1] + self.camera.position[1] - self.window.height / 2
        shoot_x = mouse_x - self.player_sprite.center_x
        shoot_y = mouse_y - self.player_sprite.center_y
        arc = AtackArc(
            pos = self.player_sprite.position, 
            vec = (shoot_x, shoot_y), 
            scale=PlayerCharacter.settings["PLAYER_ATACK_RANGE"]
        )
        self.scene.add_sprite("Effects", arc)
        collided = arcade.check_for_collision_with_list(
            arc,
            self.scene["Enemies"]
        )
        for enemy in collided: # finally remove those enemies from the game
            ans = None
            chunk_enemies = self.map.get(enemy.get_chunk()).enemies
            for key in chunk_enemies:
                if chunk_enemies[key]['sprite'] == enemy:
                    ans = key
            if ans: del chunk_enemies[ans]
            enemy.killed()

    