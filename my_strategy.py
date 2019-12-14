import model
import math


class MyStrategy:
    def __init__(self):
        pass

    def get_action(self, unit, game, debug):
        # Replace this code with your own
        def distance_sqr(a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2
        def is_on_my_side(box, unit, enemy_unit):
            if (box.position.x - unit.position.x)*(enemy_unit.position.x - unit.position.x) < 0:
                return True
            else:
                return False
        nearest_enemy = min(
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
        nearest_healthpack_onmyside = min(
            filter(lambda box: isinstance(
                box.item, model.Item.HealthPack) and is_on_my_side(box, unit, nearest_enemy), game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)
        target_pos = unit.position
        if unit.weapon is not None:
            weapon_type = unit.weapon.typ
        else:
            weapon_type = ''
        shoot = True
        swap_weapon = False
        # Target
        if unit.weapon is None and nearest_weapon is not None:
            target_pos = nearest_weapon.position
        elif unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
            # shoot = False
            # target_pos = nearest_riffle.position
            target_pos = nearest_weapon.position
            swap_weapon = True
        # elif unit.weapon is not None and weapon_type == model.WeaponType.PISTOL:
        #     target_pos = nearest_riffle.position
        #     swap_weapon = True
        # elif unit.weapon is not None and weapon_type != model.WeaponType.ASSAULT_RIFLE and distance_sqr(unit.position, nearest_riffle.position) < 1:
        #     swap_weapon = True
        #     target_pos = nearest_enemy.position
        elif unit.health < 80 and nearest_healthpack_onmyside is not None:
            target_pos = nearest_healthpack_onmyside.position
        elif unit.health < 80 and nearest_healthpack is not None:
            target_pos = nearest_healthpack.position
        elif nearest_enemy is not None:
            target_pos = nearest_enemy.position
        # debug
        # debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))
        # Aim
        aim = model.Vec2Double(0, 0)
        if nearest_enemy is not None:
            aim = model.Vec2Double(
                nearest_enemy.position.x - unit.position.x,
                nearest_enemy.position.y - unit.position.y)
        aim_c=unit.size.y / 2
        # debug.draw(model.CustomData.Line(model.Vec2Float(unit.position.x,aim_c + unit.position.y), model.Vec2Float(nearest_enemy.position.x, aim_c + nearest_enemy.position.y), 0.1, model.ColorFloat(255, 0, 0, 1)))
        delta_x = nearest_enemy.position.x - unit.position.x
        delta_y = nearest_enemy.position.y - unit.position.y - aim_c
        if abs(delta_x) > 0.5:
            k = delta_y / delta_x
            step = math.copysign(1, delta_x)
            for i in range(int(abs(delta_x))):
                point_x = int(unit.position.x) + step*i
                point_y = int(unit.position.y + k*step*i+aim_c)
                # color2 = 127
                # color1 = 0
                if game.level.tiles[int(point_x)][int(point_y)] == model.Tile.WALL:
                    shoot = False
                    # color2 = 0
                    # color1 = 127

                # debug.draw(model.CustomData.Rect(model.Vec2Float(point_x,point_y), model.Vec2Float(step, 1), model.ColorFloat(color1, color2, 0, 0.4)))
        # Jump
        jump = target_pos.y > (unit.position.y + 1)
        if abs(target_pos.x - unit.position.x)>0.001 and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
            debug.draw(model.CustomData.Log("DeltaX = {}".format(target_pos.x - unit.position.x)))
        if abs(target_pos.x - unit.position.x)>0.001 and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
            debug.draw(model.CustomData.Log("DeltaX = {}".format(target_pos.x - unit.position.x)))
        # Shooting
        reload = False
        if unit.weapon is not None and target_pos != nearest_enemy and not shoot and unit.weapon.magazine < unit.weapon.params.magazine_size:
            reload = True
            debug.draw(model.CustomData.Log(format(unit.weapon.params.reload_time)))
        # velocity
        velocity = (target_pos.x - unit.position.x) * game.properties.ticks_per_second
        # if velocity < 0 and velocity > -10:
        #     velocity = -10
        # elif velocity > 0 and velocity < 10:
        #     velocity = 10
        # if target_pos == nearest_enemy.position and abs(target_pos.x - unit.position.x)<2:
        #     # velocity = 0.2
        #     velocity = math.copysign(0.2, target_pos.x - unit.position.x)
        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=not jump,
            aim=aim,
            shoot=shoot,
            reload=False,
            swap_weapon=swap_weapon,
            plant_mine=False)
