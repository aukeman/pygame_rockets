import math
from vector2d import Vector2D

def collides_at(v, v_motion, u1, u2):


#    v + g*v_motion = u1 + h*(u2-u1)
#
#    (v + g*v_motion) x (u2-u1) = (u1 + h*(u2-u1)) x (u2-u1)
#
#    (v x (u2-u1)) + (g*v_motion x (u2-u1)) = u1 x (u2-u1) + h*(u2-u1)x(u2-u1)
#
#    (g*v_motion x (u2-u1) = (u1 x (u2-u1)) - (v x (u2-u1))
#
#    (g*v_motion x (u2-u1) = (u1 - v) x (u2-u1)
#
#    g = ((u1 - v) x (u2-u1)) / (v_motion x (u2-u1))
#

    u=(u2-u1)
    v_motion_cross_u=v_motion.cross(u)

    if v_motion_cross_u == 0.0:
        return None
    else:
        return (u1-v).cross(u) / v_motion_cross_u


def find_collision_point(v, v_motion, u1, u2):

    g=collides_at(v, v_motion, u1, u2)

    if g is not None and 0.0 <= g <= 1.0:
        h=collides_at(u1, u2-u1, v, v+v_motion)

        if h is not None and 0.0 <= h <= 1.0:
            return (v+g*v_motion)

    return None

class BoundingPolygon:

    def __init__(self,
                 vertices,
                 origin=(0.0,0.0),
                 position=(0.0,0.0),
                 angle=0.0,
                 scale=(1.0,1.0)):
        self.vertices=map(lambda v: Vector2D(v[0],v[1]), vertices)
        self.origin=Vector2D(origin[0],origin[1])
        self.position=Vector2D(position[0],position[1])
        self.angle=angle
        self.scale=Vector2D(scale[0],scale[1])

        self.update()
        

    def copy(self):
        return BoundingPolygon(self.vertices,
                               self.origin,
                               self.position,
                               self.angle,
                               self.scale)

    def _transform_vertex(self, vertex):
        xfrm_v=Vector2D(vertex[0], vertex[1])

        # scale
        xfrm_v.x *= self.scale.x
        xfrm_v.y *= self.scale.y

        # rotate
        theta = math.radians(self.angle)
        new_x = xfrm_v.x*math.cos(theta) - xfrm_v.y*math.sin(theta)
        new_y = xfrm_v.x*math.sin(theta) + xfrm_v.y*math.cos(theta)
        
        xfrm_v.x = new_x
        xfrm_v.y = new_y

        # translate
        xfrm_v += (self.position-self.origin)

        return xfrm_v

    def _transform_vertices(self):
        return [self._transform_vertex(v) for v in self.vertices]

    def _calculate_axis_aligned_bounding_box(self):

        self.lower_left=Vector2D( min(self.transformed_vertices,
                                      key=lambda v: v.x),
                                  
                                  min(self.transformed_vertices,
                                      key=lambda v: v.y) )

        self.upper_right=Vector2D( max(self.transformed_vertices,
                                       key=lambda v: v.x),
                                   
                                   max(self.transformed_vertices,
                                       key=lambda v: v.y) )


    def update(self):
        self.transformed_vertices=self._transform_vertices()
        self.transformed_sides=zip(self.transformed_vertices,
                                   self.transformed_vertices[1:] + self.transformed_vertices[:1])

        self._calculate_axis_aligned_bounding_box()

    def test_collision( self, p, p_motion ):

        min_collision_at=None

        for v1,v2 in self.transformed_sides:

            collision_point=find_collision_point(p, p_motion, v1, v2)

            if collision_point is not None:
                return collision_point

        return None

    def test_bounding_polygon_collision(self, other):

        # axis aligned bounding-box check first
        if not ( other.lower_left.x > self.upper_right.x or
                 other.upper_right.x < self.lower_left.x or
                 other.lower_left.y > self.upper_right.y or
                 other.upper_right.y < self.lower_left.y ):

            # check the bounding polygon
            for v1,v2 in other.transformed_sides:
                collision_point = self.test_collision(v1, v2-v1)
                
                if collision_point is not None:
                    return collision_point

        return None
        

#     def test_motion(self, moved_bounding_polygon, other):

#         other_xfrmed_vertices=other._transform_vertices()

#         other_sides=zip(other_xfrmed_vertices,
#                         other_xfrmed_vertices[1:]+other.vertices[:1])

#         earliest_collision=9999.9

#         for v1, v2 in zip(self._transform_vertices(),
#                           moved_bounding_polygon.transform_vertices()):
#             for u1, u2 in other_sides:
#                 c=collides_at( v1, v2-v1, u1, u2 )

#                 if ( c is not None and 0.0 <= c < earliest_collision ):
#                     earliest_collision = c

#         if earliest_collision == 9999.9:
#             return None
#         else:
#             return earliest_collision
                

if __name__=="__main__":

    bounding_box=BoundingPolygon( (Vector2D(-1.0, -1.0),
                                   Vector2D(1.0, -1.0),
                                   Vector2D(1.0, 1.0),
                                   Vector2D(-1.0, 1.0)) )

    bounding_box.position=Vector2D(1.0, 1.0)
    bounding_box.angle=45.0
    

    bounding_box.update()


    print bounding_box.test_collision( Vector2D(-2.0, 0.0),
                                       Vector2D(4.0, 0.0) )
