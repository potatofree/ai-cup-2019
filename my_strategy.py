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
                    # debug.(model.CustomData.Rect(model.Vec2Float(point_x, point_y), model.Vec2Float(step, 1), model.ColorFloat(0, 125, 0, 0.4)))
            return is_visible

        def friendly_fire(u1, u2, aim):
            t = Vec2Double(aim.x + u1.x, aim.y + u1.y)
            friendly_fire = False
            delta_x = t.x - u1.x
            delta_y = t.y - u1.y
            if abs(delta_x) > 0.01:
                k = delta_y / delta_x
                if u1.y + k*(u2.x-u1.x-0.4) > u2.y and u1.y + k*(u2.x-u1.x-0.4) < u2.y +1.8 and abs(delta_x)>abs(t.x - u2.x):
                    friendly_fire = True
                if u1.y + k*(u2.x-u1.x+0.4) > u2.y and u1.y + k*(u2.x-u1.x+0.4) < u2.y +1.8 and abs(delta_x)>abs(t.x - u2.x):
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

        def bullet_predict(bullet, mticks):
            # mticks = ticks * game.properties.updates_per_tick
            bullet_predict = Vec2Double(bullet.position.x, bullet.position.y)
            speed_h = (bullet.velocity.x / game.properties.ticks_per_second) / game.properties.updates_per_tick
            speed_v = (bullet.velocity.y / game.properties.ticks_per_second) / game.properties.updates_per_tick
            bullet_predict.x = bullet.position.x + speed_h * mticks
            bullet_predict.y = bullet.position.y + speed_v * mticks
            return bullet_predict

        def is_bullet_in_unit (bullet, bullet_pos, unit_pos):
            is_bullet_in_unit = False
            bullet_x = list()
            bullet_y = list()
            unit_x = list()
            unit_y = list()
            for i in (-1, 1):
                bullet_x.append(bullet_pos.x + i * 0.5*bullet.size)
                bullet_y.append(bullet_pos.y + i * 0.5*bullet.size)
                unit_x.append(unit_pos.x + i * 0.5*game.properties.unit_size.x)
            unit_y.append(unit_pos.y)
            unit_y.append(unit_pos.y + game.properties.unit_size.y)
            for i in range(2):
                for j in range(2):
                    if unit_x[0] <= bullet_x[i] <= unit_x[1] and unit_y[0] <= bullet_y[j] <= unit_y[1]:
                        is_bullet_in_unit = True
                        return is_bullet_in_unit
            return is_bullet_in_unit

        def unit_predict (unit, velocity, jump, mticks):
            # mticks = ticks * game.properties.updates_per_tick
            unit_predict = Vec2Double(unit.position.x, unit.position.y)
            speed_fall = - (game.properties.unit_fall_speed / game.properties.ticks_per_second) / game.properties.updates_per_tick
            speed_h = (velocity / game.properties.ticks_per_second) / game.properties.updates_per_tick
            jump_time = mticks
            if jump:
                speed_v = (game.properties.unit_jump_speed / game.properties.ticks_per_second) / game.properties.updates_per_tick
            else:
                speed_v = 0
            if not jump and unit.jump_state.can_jump and unit.jump_state.max_time < game.properties.unit_jump_time:
                speed_v = speed_fall
            if jump and unit.jump_state.can_jump:
                jump_time = unit.jump_state.max_time * game.properties.ticks_per_second * game.properties.updates_per_tick
            unit_predict.x = unit.position.x + speed_h*mticks
            if mticks > jump_time:
                unit_predict.y = unit.position.y + speed_v*jump_time + speed_fall*(mticks - jump_time)
            else:
                unit_predict.y = unit.position.y + speed_v*mticks
            return unit_predict

        def target_enemy_pos(unit, enemy):
            target_enemy_pos = Vec2Double(enemy.x, enemy.y)
            target = False
            enemy_pos = target_enemy_pos
            unit_pos = Vec2Double(unit.x, unit.y)
            max_x = len(game.level.tiles)
            max_y = len(game.level.tiles[0])
            # enemy_pos.y = enemy_pos.y + 0.9
            point = Vec2Double(0, 0)
            tile = Vec2Double(0, 0)
            nearest_pos = enemy_pos
            dist = distance_sqr(unit_pos, enemy_pos)
            for a in range(3,-1,-1):
                for b in range(2*a,-1,-1):
                    for sign in (((1,-1),(-1, 0)),((-1, 0),(1, -1)),((1, 0), (1, -1)),((1, -1),(1, 0))):
                        tile.x = enemy_pos.x + a*sign[0][0] + b*sign[0][1]
                        tile.y = enemy_pos.y + a*sign[1][0] + b*sign[1][1]
                        if 1 > tile.x or tile.x > max_x-1: continue
                        if 1 > tile.y or tile.y > max_y-1: continue
                        point.x = tile.x + 0.5
                        point.y = tile.y + 0.5
                        if is_visible(point, enemy_pos):
                            # debug.draw(model.CustomData.Rect(model.Vec2Float(tile.x, tile.y), model.Vec2Float(1, 1), model.ColorFloat(0, 150, 0, 0.3)))
                            if distance_sqr(unit_pos, point) < dist:
                                target = True
                                dist = distance_sqr(unit_pos, point)
                                nearest_pos = Vec2Double(point.x, point.y)
                        # else:
                            # debug.draw(model.CustomData.Rect(model.Vec2Float(tile.x, tile.y), model.Vec2Float(1, 1), model.ColorFloat(150, 0, 0, 0.3)))
                if target: break

            # debug.draw(model.CustomData.Rect(model.Vec2Float(nearest_pos.x, nearest_pos.y), model.Vec2Float(1, 1), model.ColorFloat(250, 150, 100, 0.9)))
            return nearest_pos

        enemies = [e for e in game.units if e.player_id != unit.player_id]
        bullets = [b for b in game.bullets if b.player_id != unit.player_id]
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
                    # target_pos = nearest_enemy.position
                    target_pos = target_enemy_pos(unit.position, nearest_enemy.position)
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
                    # target_pos = target_enemy_pos(unit.position, nearest_enemy.position)

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
            # debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(body.x, body.y), 0.1, model.ColorFloat(255, 0, 0, 1)))
            # debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(head.x, head.y), 0.02, model.ColorFloat(0, 255, 0, 1)))
            # debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(legs.x, legs.y), 0.02, model.ColorFloat(0, 0, 255, 1)))
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

        # if shoot:
            # debug.draw(model.CustomData.Line(model.Vec2Float(shooting_point.x,shooting_point.y), model.Vec2Float(aim.x + shooting_point.x, aim.y + shooting_point.y), 0.3 , model.ColorFloat(255, 0, 255, 1)))
            # debug.draw(model.CustomData.Log('DeltaX {}'.format(delta_x)))
            # debug.draw(model.CustomData.Log('DeltaY {}'.format(delta_y)))
        # if unit.weapon is not None:
        #     debug.draw(model.CustomData.Log('Magazine {}'.format(unit.weapon.magazine)))
        #     debug.draw(model.CustomData.Log('Timer {}'.format(unit.weapon.fire_timer)))
        #
        # if nearest_healthpack_onmyside is not None:
        #     debug.draw(model.CustomData.Rect(model.Vec2Float(nearest_healthpack_onmyside.position.x, nearest_healthpack_onmyside.position.y), model.Vec2Float(1, 1), model.ColorFloat(125, 0, 125, 0.4)))
        #     debug.draw(model.CustomData.Rect(model.Vec2Float(target_pos.x, target_pos.y), model.Vec2Float(1, 1), model.ColorFloat(125, 125, 0, 0.4)))
        # # Jump
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
            # debug.draw(model.CustomData.Log(format(unit.weapon.params.reload_time)))
        # velocity

        # debug.draw(model.CustomData.Log("Stand = {}".format(unit.stand)))

        target = Vec2Double(aim.x + shooting_point.x, aim.y + shooting_point.y)
        if teammate is not None:
            Storage.Am_i_second = not Storage.Am_i_second
            if friendly_fire(shooting_point, teammate.position, aim):
                # debug.draw(model.CustomData.Rect(model.Vec2Float(unit.position.x, unit.position.y), model.Vec2Float(-1, 1), model.ColorFloat(125, 125, 0, 0.4)))
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
        if velocity > game.properties.unit_max_horizontal_speed :
            velocity = game.properties.unit_max_horizontal_speed
        elif velocity < -game.properties.unit_max_horizontal_speed:
            velocity = -game.properties.unit_max_horizontal_speed
        debug.draw(model.CustomData.Log('Velocity {}'.format(velocity)))

        def collision (bullet, unit, velocity, jump, ticks):
            collision = [False, 0]
            ticks_pred = ticks
            mticks_pred = ticks_pred * game.properties.updates_per_tick
            for mt in range(mticks_pred):
                bullet_pr_pos = bullet_predict(b, mt)
                unit_pr_pos = unit_predict(unit, velocity, jump, mt)
                # debug.draw(model.CustomData.Rect(model.Vec2Float(unit_pr_pos.x - 0.4, unit_pr_pos.y), model.Vec2Float(0.8, 1.8), model.ColorFloat(0, 125, 0, 0.2)))
                # debug.draw(model.CustomData.Rect(model.Vec2Float(bullet_pr_pos.x -b.size/2, bullet_pr_pos.y - b.size/2), model.Vec2Float(b.size, b.size), model.ColorFloat(0.4, 0, 0, 0.2)))
                if is_bullet_in_unit(b, bullet_pr_pos, unit_pr_pos):
                    # debug.draw(model.CustomData.Log('Collision in {} ticks'.format(int(mt))))
                    collision[0] = True
                    collision[1] = mt
                    break
            return collision
        depth = 10
        state = [(copysign(game.properties.unit_max_horizontal_speed, velocity), jump),
                    (copysign(game.properties.unit_max_horizontal_speed, velocity), not jump),
                    (velocity, not jump),
                    (copysign(game.properties.unit_max_horizontal_speed, -velocity), jump),
                    (-velocity, jump),
                    (-velocity, not jump),
                    (copysign(game.properties.unit_max_horizontal_speed, -velocity), not jump)]
        # print(game.current_tick, unit.jump_state)
        for b in bullets:
            # debug.draw(model.CustomData.Log(format(b)))
            # print(velocity, jump)
            if collision(b, unit, velocity, jump, depth)[0]:
                for st in state:
                    variant = collision(b, unit, st[0], st[1], depth)
                    # print(game.current_tick, variant)
                    if not variant[0]:
                        # print(st)
                        velocity = st[0]
                        jump = st[1]
                        break

        return model.UnitAction(
            velocity=velocity,
            jump=jump,
            jump_down=not jump,
            aim=aim,
            shoot=shoot,
            reload=False,
            swap_weapon=swap_weapon,
            plant_mine=False)
