import model
import math
from math import copysign, floor
from model import Vec2Double
from random import uniform, random
class Storage:
    enemy = list()
    enemy_ids = {}
    tick_saved = -1
    Am_i_second = False




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
            if delta_x == 0: return is_visible
            k = delta_y / delta_x
            M = 10
            step = copysign(1/M, delta_x)
            for i in range(int(floor(abs(delta_x))*M+1)):
                point_x = a.x + step*i
                point_y = a.y + k*step*i
                if game.level.tiles[int(floor(point_x))][int(floor(point_y))] == model.Tile.WALL:
                    is_visible = False
                    # debug.draw(model.CustomData.Rect(model.Vec2Float(point_x, point_y), model.Vec2Float(step, 1), model.ColorFloat(125, 0, 0, 0.4)))
                # else:
                    # debug.draw(model.CustomData.Rect(model.Vec2Float(point_x, point_y), model.Vec2Float(step, 1), model.ColorFloat(0, 125, 0, 0.4)))
            return is_visible

        def friendly_fire(u1, u2, aim):
            t = Vec2Double(aim.x + u1.x, aim.y + u1.y)
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

        def predict(enemy, ticks):
            predict = Vec2Double(enemy.position.x, enemy.position.y)
            id = Storage.enemy_ids[enemy.id]
            prev_pos = Storage.enemy[id][game.current_tick-1][0]
            delta_x = enemy.position.x - prev_pos.x
            delta_y = enemy.position.y - prev_pos.y
            jump_change = Storage.enemy[id][game.current_tick-1][1].speed != enemy.jump_state.speed
            jump = Storage.enemy[id][game.current_tick][1].speed * Storage.enemy[id][game.current_tick][1].max_time
            predict.x = enemy.position.x + ticks * delta_x
            if ticks * delta_y > jump:
                 predict.y = enemy.position.y + jump
            else:
                 predict.y = enemy.position.y + ticks * delta_y
            return predict

        def save_state(enemy):
            id = Storage.enemy_ids[enemy.id]
            Storage.enemy[id].append((Vec2Double(enemy.position.x, enemy.position.y), enemy.jump_state))
            pass

        enemies = [e for e in game.units if e.player_id != unit.player_id]
        nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        teammate = min(
            filter(lambda u: u.player_id == unit.player_id and u.id != unit.id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)

        if game.current_tick > Storage.tick_saved:
            Storage.tick_saved = game.current_tick
            #initial
            if game.current_tick == 0:
                i = 0
                for en in filter(lambda u: u.player_id != unit.player_id, game.units):
                    Storage.enemy_ids[en.id] = i
                    i = i + 1
                    Storage.enemy.append([])
            #state saving
            for en in filter(lambda u: u.player_id != unit.player_id, game.units):
                save_state(en)


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
        nearest_pistol = min(
        filter(lambda box: isinstance(
            box.item, model.Item.Weapon) and box.item.weapon_type == model.WeaponType.PISTOL, game.loot_boxes),
        key=lambda box: distance_sqr(box.position, unit.position),
        default=None)
        nearest_rocket = min(
        filter(lambda box: isinstance(
            box.item, model.Item.Weapon) and box.item.weapon_type == model.WeaponType.ROCKET_LAUNCHER, game.loot_boxes),
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
        if not Storage.Am_i_second:
            if unit.weapon is None and nearest_weapon is not None:
                target_pos = nearest_weapon.position
                if nearest_pistol is not None and abs(distance_sqr(unit.position, nearest_weapon.position) - distance_sqr(unit.position, nearest_pistol.position)) < 2:
                    target_pos = nearest_pistol.position
            elif unit.weapon is not None:
                if teammate is not None and teammate.weapon is None:
                    target_pos = nearest_enemy.position
                # print(distance_sqr(unit.position, nearest_pistol.position))
                elif nearest_pistol is not None and unit.weapon.typ == model.WeaponType.ROCKET_LAUNCHER and distance_sqr(unit.position, nearest_pistol.position) <= 40:
                    target_pos = nearest_pistol.position
                    swap_weapon = True
                elif nearest_pistol is not None and unit.weapon.typ == model.WeaponType.ROCKET_LAUNCHER and distance_sqr(unit.position, nearest_nonrocket.position) <= 9:
                    if nearest_nonrocket is not None:
                        target_pos = nearest_nonrocket.position
                    elif nearest_weapon is not None:
                        target_pos = nearest_weapon.position
                    swap_weapon = True
                elif nearest_pistol is not None and unit.weapon.typ == model.WeaponType.ASSAULT_RIFLE and distance_sqr(unit.position, nearest_pistol.position) <= 64:
                    target_pos = nearest_pistol.position
                    swap_weapon = True
                    if nearest_rocket is not None and distance_sqr(unit.position, nearest_rocket.position) <= 1:
                        swap_weapon = False
                elif unit.health < 80 and nearest_healthpack_onmyside is not None:
                    target_pos = nearest_healthpack_onmyside.position
                elif unit.health < 80 and nearest_healthpack is not None:
                    target_pos = nearest_healthpack.position
                elif nearest_enemy is not None:
                    target_pos = nearest_enemy.position
        else:
            if unit.weapon is None and nearest_weapon is not None:
                target_pos = nearest_weapon.position
            elif unit.weapon is not None:
                if teammate is not None and teammate.weapon is None:
                    print
                    target_pos = nearest_enemy.position
                elif nearest_nonrocket is not None and unit.weapon.typ == model.WeaponType.ROCKET_LAUNCHER and distance_sqr(unit.position, nearest_nonrocket.position) <= 40:
                    target_pos = nearest_nonrocket.position
                    swap_weapon = True
                elif nearest_pistol is not None and unit.weapon.typ == model.WeaponType.ASSAULT_RIFLE and distance_sqr(unit.position, nearest_pistol.position) <= 16:
                    target_pos = nearest_pistol.position
                    swap_weapon = True
                    if nearest_rocket is not None and distance_sqr(unit.position, nearest_rocket.position) <= 1:
                        swap_weapon = False
                elif unit.health < 80 and nearest_healthpack_onmyside is not None:
                    target_pos = nearest_healthpack_onmyside.position
                elif unit.health < 80 and nearest_healthpack is not None:
                    target_pos = nearest_healthpack.position
                elif nearest_enemy is not None:
                    target_pos = nearest_enemy.position

        # Aim
        target_enemy = nearest_enemy

        aim = model.Vec2Double(0, 0)
        aim_c=unit.size.y / 2
        shooting_point = model.Vec2Double(unit.position.x, unit.position.y + aim_c)
        head = model.Vec2Double(0, 0)
        legs = model.Vec2Double(0, 0)
        body = model.Vec2Double(0, 0)
        p = copysign(1, delta_x)
        enemies.sort(key=lambda e: e.health)
        if len(enemies)>1 and enemies[0].health<=50:
            lowest_enemy = enemies[0]
            if is_visible(shooting_point, lowest_enemy.position):
                target_enemy = lowest_enemy

        if target_enemy is not None:
            aim = model.Vec2Double(target_enemy.position.x - unit.position.x,
                                   target_enemy.position.y - unit.position.y)
            head.x = target_enemy.position.x
            head.y = target_enemy.position.y + unit.size.y
            legs.x = head.x
            legs.y = target_enemy.position.y
            body.x = head.x
            body.y = target_enemy.position.y + 0.5*unit.size.y
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(body.x, body.y), 0.1, model.ColorFloat(255, 0, 0, 1)))
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(head.x, head.y), 0.02, model.ColorFloat(0, 255, 0, 1)))
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(legs.x, legs.y), 0.02, model.ColorFloat(0, 0, 255, 1)))
        if abs(delta_x) > 0.5:
            shoot = is_visible(shooting_point, legs)
            if unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
                shoot = is_visible(shooting_point, legs) and is_visible(shooting_point, body) and is_visible(shooting_point, head)
            if unit.weapon is not None and weapon_type != model.WeaponType.ROCKET_LAUNCHER:
                if is_visible(shooting_point, body):
                    shoot = True
                    aim.x = head.x - shooting_point.x
                    aim.y = head.y - shooting_point.y
                if is_visible(shooting_point, legs):
                    shoot = True
                    aim.x = body.x - shooting_point.x
                    aim.y = body.y - shooting_point.y
        if abs(delta_x) > 2 and unit.weapon is not None:
            ticks = int(0.8 * abs(delta_x) / (unit.weapon.params.bullet.speed/game.properties.ticks_per_second))
            # print(unit.weapon.params.bullet.speed, game.properties.ticks_per_second, ticks)
            if ticks >=15: ticks = 15
            pred = predict(target_enemy, ticks)
            corr = Vec2Double(pred.x - legs.x, pred.y - legs.y)
            aim.x = aim.x + corr.x
            aim.y = aim.y + corr.y

        if shoot:
            debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(aim.x + shooting_point.x, aim.y + shooting_point.y), 0.3 , model.ColorFloat(255, 0, 255, 1)))
            # debug.draw(model.CustomData.Log('DeltaX {}'.format(delta_x)))
            # debug.draw(model.CustomData.Log('DeltaY {}'.format(delta_y)))
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
            # debug.draw(model.CustomData.Log("DeltaX = {}".format(target_pos.x - unit.position.x)))
        if abs(target_pos.x - unit.position.x)>0.001 and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
            # debug.draw(model.CustomData.Log("DeltaX = {}".format(target_pos.x - unit.position.x)))
        # Shooting
        reload = False
        if unit.weapon is not None and target_pos != target_enemy.position and not shoot and unit.weapon.magazine < unit.weapon.params.magazine_size:
            reload = True
            debug.draw(model.CustomData.Log(format(unit.weapon.params.reload_time)))
        # velocity

        debug.draw(model.CustomData.Log("Stand = {}".format(unit.stand)))

        target = Vec2Double(aim.x + shooting_point.x, aim.y + shooting_point.y)
        if teammate is not None:
            Storage.Am_i_second = not Storage.Am_i_second
            if friendly_fire(shooting_point, teammate.position, aim):
                debug.draw(model.CustomData.Rect(model.Vec2Float(unit.position.x, unit.position.y), model.Vec2Float(-1, 1), model.ColorFloat(125, 125, 0, 0.4)))
                shoot = False
                jump = True
            if unit.weapon is not None and weapon_type == model.WeaponType.ROCKET_LAUNCHER:
                # shoot = False
                swap_weapon = True
                target_pos = nearest_nonrocket.position
                if teammate.weapon is None:
                    # swap_weapon = False
                    target_pos = nearest_enemy.position
        else:
            Storage.Am_i_second = False

        # if unit.stand and not shoot and unit.weapon is not None:
        #     if target_pos.x > unit.position.x:
        #         target_pos.x = uniform(0, unit.position.x)
        #         jump = True
        #     else:
        #         target_pos.x = uniform(unit.position.x, len(game.level.tiles))
        #         jump = True

        velocity = (target_pos.x - unit.position.x) * game.properties.ticks_per_second

        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=not jump,
            aim=aim,
            shoot=shoot,
            reload=False,
            swap_weapon=swap_weapon,
            plant_mine=False)
