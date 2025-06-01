from visuscript.primatives import Vec2, Vec3

def magnitude(vec: Vec2 | Vec3):
    return vec.dot(vec)**0.5
