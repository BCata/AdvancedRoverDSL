from api.wheel_movement import move_both_for_seconds
from ev3dev2.sound import Sound

s = Sound()


def celebrate(celebration="sing"):
    if celebration == "sing":
        s.play('resources/celebration_song.wav')
    elif celebration == "spin":
        print("spin")
        move_both_for_seconds(30, 2.3, True, -30)
