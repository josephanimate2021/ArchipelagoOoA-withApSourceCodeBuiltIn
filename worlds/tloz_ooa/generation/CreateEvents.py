from ..Options import *

def create_events(world):
    world.create_event("maku seed", "Maku Seed")

    if world.options.goal == OraclesGoal.option_beat_vanila_boss:
        world.create_event("veran beaten", "_beaten_game")
    elif world.options.goal == OraclesGoal.option_beat_ganon:
        world.create_event("ganon beaten", "_beaten_game")

    world.create_event("ridge move vine seed", "_access_cart")

    world.create_event("d3 S crystal", "_d3_S_crystal")
    world.create_event("d3 E crystal", "_d3_E_crystal")
    world.create_event("d3 W crystal", "_d3_W_crystal")
    world.create_event("d3 N crystal", "_d3_N_crystal")
    world.create_event("d3 B1F spinner", "_d3_B1F_spinner")

    world.create_event("d6 wall B bombed", "_d6_wall_B_bombed")
    world.create_event("d6 canal expanded", "_d6_canal_expanded")

    world.create_event("d7 boss", "_finished_d7")