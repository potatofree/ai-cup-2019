import model
import math
from math import copysign
from model import Vec2Double


class MyStrategy:
    def __init__(self):
        pass

    def get_action(self, unit, game, debug):
        # Replace this code with your own
        def distance_sqr(a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2
        def is_on_my_side(box, unit, enemy_unit):
            if (box.position.x - enemy_unit.position.x)*(unit.position.x - enemy_unit.position.x) > 0:
                return True
            else:
                return False
        def is_visible(a, b):
            is_visible = True
            delta_x = b.x - a.x
            delta_y = b.y - a.y
            k = delta_y / delta_x
            step = math.copysign(1, delta_x)
            for i in range(int(abs(delta_x))):
                point_x = int(a.x) + step*i
                point_y = int(a.y + k*step*i)
                if game.level.tiles[int(point_x)][int(point_y)] == model.Tile.WALL:
                    is_visible = False
            return is_visible
        def friendly_fire(u1, u2, t):
            friendly_fire = False
            delta_x = t.x - u1.x
            delta_y = t.y - u1.y
            if abs(delta_x) > 0.01:
                k = delta_y / delta_x
                if u1.y + k*(u2.x-u1.x) > u2.y and u1.y + k*(u2.x-u1.x) < u2.y +1.8 and abs(delta_x)>abs(t.x - u2.x):
                    # print (u2.y, (u1.y + k*(u2.x-u1.x)) , u2.y+1.8)
                    friendly_fire = True
            elif u1.y < u2.y < t.y or u1.y > u2.y > t.y:
                friendly_fire = True
            if delta_x > 0.7 and friendly_fire and (t.x - u1.x)*(t.x - u2.x) < 0:
                friendly_fire = False
            return friendly_fire

        nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        teammate = min(
            filter(lambda u: u.player_id == unit.player_id and u.id != unit.id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        delta_x = nearest_enemy.position.x - unit.position.x
        delta_y = nearest_enemy.position.y - unit.position.y

        nearest_weapon = min(
            filter(lambda box: isinstance(
                box.item, model.Item.Weapon), game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)
        # nearest Riffle
        nearest_nonrocket = min(
        filter(lambda box: isinstance(
            box.item, model.Item.Weapon) and box.item.weapon_type != model.WeaponType.ROCKET_LAUNCHER, game.loot_boxes),
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
        # aim = model.Vec2Double(0, 0)
        # if nearest_enemy is not None:
        #     aim = model.Vec2Double(
        #         nearest_enemy.position.x - unit.position.x,
        #         nearest_enemy.position.y - unit.position.y)
        # aim_c=unit.size.y / 2
        # delta_x = nearest_enemy.position.x - unit.position.x
        # delta_y = nearest_enemy.position.y - unit.position.y - aim_c
        # if abs(delta_x) > 0.5:
        #     k = delta_y / delta_x
        #     step = math.copysign(1, delta_x)
        #     for i in range(int(abs(delta_x))):
        #         point_x = int(unit.position.x) + step*i
        #         point_y = int(unit.position.y + k*step*i+aim_c)
        #         # color2 = 127
        #         # color1 = 0
        #         if game.level.tiles[int(point_x)][int(point_y)] == model.Tile.WALL:
        #             shoot = False
        #             # color2 = 0
        #             # color1 = 127
        aim = model.Vec2Double(0, 0)
        aim_c=unit.size.y / 2
        shooting_point = model.Vec2Double(unit.position.x, unit.position.y + aim_c)
        head = model.Vec2Double(0, 0)
        legs = model.Vec2Double(0, 0)
        body = model.Vec2Double(0, 0)
        p = copysign(1, delta_x)
        if nearest_enemy is not None:
            aim = model.Vec2Double(nearest_enemy.position.x - unit.position.x,
                                   nearest_enemy.position.y - unit.position.y)
            head.x = nearest_enemy.position.x
            head.y = nearest_enemy.position.y + unit.size.y
            legs.x = head.x
            legs.y = nearest_enemy.position.y
            body.x = head.x
            body.y = nearest_enemy.position.y + 0.5*unit.size.y
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(body.x, body.y), 0.1, model.ColorFloat(255, 0, 0, 1)))
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(head.x, head.y), 0.02, model.ColorFloat(0, 255, 0, 1)))
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(legs.x, legs.y), 0.02, model.ColorFloat(0, 0, 255, 1)))
        if abs(delta_x) > 0.5:
            shoot = is_visible(shooting_point, legs)
            if unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
                shoot = is_visible(shooting_point, legs) and is_visible(shooting_point, body) and is_visible(shooting_point, head)
            if unit.weapon is not None and weapon_type != model.WeaponType.ROCKET_LAUNCHER:
                # if is_visible(shooting_point, body):
                #     shoot = True
                #     aim.x = head.x - shooting_point.x
                #     aim.y = head.y - shooting_point.y
                if is_visible(shooting_point, legs):
                    shoot = True
                    aim.x = body.x - shooting_point.x
                    aim.y = body.y - shooting_point.y
        if shoot:
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(aim.x + shooting_point.x, aim.y + shooting_point.y), 0.3 , model.ColorFloat(255, 0, 255, 1)))
            debug.draw(model.CustomData.Log('DeltaX {}'.format(delta_x)))
            debug.draw(model.CustomData.Log('DeltaY {}'.format(delta_y)))
        if unit.weapon is not None:
            debug.draw(model.CustomData.Log('Magazine {}'.format(unit.weapon.magazine)))
            debug.draw(model.CustomData.Log('Timer {}'.format(unit.weapon.fire_timer)))

        if nearest_healthpack_onmyside is not None:
            debug.draw(model.CustomData.Rect(model.Vec2Float(nearest_healthpack_onmyside.position.x, nearest_healthpack_onmyside.position.y), model.Vec2Float(1, 1), model.ColorFloat(125, 0, 125, 0.4)))
            debug.draw(model.CustomData.Rect(model.Vec2Float(target_pos.x, target_pos.y), model.Vec2Float(1, 1), model.ColorFloat(125, 125, 0, 0.4)))
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


        target = Vec2Double(aim.x + shooting_point.x, aim.y + shooting_point.y)
        if teammate is not None:
            if friendly_fire(unit.position, teammate.position, target):
                shoot = False
                jump = True
            if unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
                # shoot = False
                target_pos = nearest_nonrocket.position
                if teammate.weapon is None:
                    swap_weapon = False
                    target_pos = nearest_enemy.position
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
