import model
import math

class MyStrategy:
    def __init__(self):
        pass

    def get_action(self, unit, game, debug):
        # Replace this code with your own
        def distance_sqr(a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2
        nearest_enemy = min(
            # [u for u in game.units if u.player_id != ...]
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        nearest_weapon = min(
            filter(lambda box: isinstance(
                box.item, model.Item.Weapon), game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)
        # nearest Riffle
        nearest_riffle = min(
        filter(lambda box: isinstance(
            box.item, model.Item.Weapon) and box.item.weapon_type == model.WeaponType.ASSAULT_RIFLE, game.loot_boxes),
        key=lambda box: distance_sqr(box.position, unit.position),
        default=None)
        # nearest healthpack
        nearest_healthpack = min(
            filter(lambda box: isinstance(
                box.item, model.Item.HealthPack), game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)
        target_pos = unit.position
        if unit.weapon is not None:
            weapon_type = unit.weapon.typ
            # if weapon_type == model.WeaponType.ASSAULT_RIFLE:
            #     print('Ruzzho')
            # elif weapon_type == model.WeaponType.PISTOL:
            #     print('Pistik')
            # elif weapon_type == model.WeaponType.ROCKET_LAUNCHER:
            #     print('Bazuka')
            # print(weapon_type)
        else:
             weapon_type = ''
        shoot = True
        swap_weapon = False
        # Weapon
        if unit.weapon is None and nearest_weapon is not None:
            target_pos = nearest_weapon.position
        elif unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
            shoot = False
            target_pos = nearest_riffle.position
            swap_weapon = True
        elif unit.weapon is not None and weapon_type == model.WeaponType.PISTOL:
            target_pos = nearest_riffle.position
            swap_weapon = True
        elif unit.weapon is not None and weapon_type != model.WeaponType.ASSAULT_RIFLE and distance_sqr(unit.position, nearest_riffle.position) < 1:
            swap_weapon = True
            target_pos = nearest_enemy.position
        elif unit.health < 80 and nearest_healthpack is not None:
            target_pos = nearest_healthpack.position
        elif nearest_enemy is not None:
            target_pos = nearest_enemy.position
        # debug
        debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))
        # Aim
        aim = model.Vec2Double(0, 0)
        if nearest_enemy is not None:
            aim = model.Vec2Double(
                nearest_enemy.position.x - unit.position.x,
                nearest_enemy.position.y - unit.position.y)
        # Jump
        jump = target_pos.y > unit.position.y
        if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
        if target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
        # if target_pos == nearest_enemy.position:
        #     jump = True
        # velocity
        velocity = target_pos.x - unit.position.x
        if velocity < 0 and velocity > -10:
            velocity = -10
        elif velocity > 0 and velocity < 10:
            velocity = 10
        if target_pos == nearest_enemy.position and abs(target_pos.x - unit.position.x)<2:
            # velocity = 0.2
            velocity = math.copysign(0.2, target_pos.x - unit.position.x)
        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=not jump,
            aim=aim,
            shoot=shoot,
            reload=False,
            swap_weapon=swap_weapon,
            plant_mine=False)
