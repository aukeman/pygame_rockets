import math

_vector_pool=[]

class Vector2D(object):


    def __new__(cls, *args, **kwargs):
        if 0 < len(_vector_pool):
            return _vector_pool.pop()
        else:
            return super(Vector2D, cls).__new__(cls)

    def __del__(self):
        if _vector_pool is not None:
            _vector_pool.append(self)

    def __init__(self, x, y):
        self.x=x
        self.y=y

    def length(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))

    def dot(self, other):
        return (self.x*other[0])+(self.y*other[1])

    def cross(self, other):
        return (self.x*other[1])-(self.y*other[0])

    def normalized(self):
        result=Vector2D(self.x,self.y)
        result /= float(self)

        return result

    def normalize(self):
        magnitude=float(self)

        self.x /= magnitude
        self.y /= magnitude

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        else:
            return None

    def __setitem__(self, idx, value):
        if idx == 0:
            self.x=value
            return self
        elif idx == 1:
            self.y=value
            return self
    
    def __add__(self, other):
        return Vector2D( x=(self.x+other[0]), y=(self.y+other[1])  )

    def __radd__(self, other):
        return self+other

    def __iadd__(self, other):
        self.x += other[0]
        self.y += other[1]
        return self

    def __sub__(self, other):
        return Vector2D( x=(self.x-other[0]), y=(self.y-other[1]) )

    def __rsub__(self, other):
        return Vector2D( x=(other[0]-self.x), y=(other[1]-self.y) )

    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        return self

    def __mul__(self, scalar):
        return Vector2D( x=(self.x*scalar), y=(self.y*scalar) )

    def __rmul__(self, scalar):
        return self*scalar

    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    def __div__(self,scalar):
        return Vector2D( x=(self.x/scalar), y=(self.y/scalar) )

    def __idiv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
        return self

    def __neg__(self):
        return -1.0*self
        
    def __float__(self):
        return self.length()

    def __eq__(self, other):
        return (self.x == other[0] and self.y == other[1])

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.x, other.x))

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

if __name__ == "__main__":

    v1=Vector2D( 1.0, 0.0 )
    v2=Vector2D( 0.0, 1.0 )

    v3=Vector2D( 1.0, 1.0 )

    if (v1 + v2) != Vector2D(1.0, 1.0):
        raise "Failed addition"

    elif (v1 - v2) != Vector2D(1.0, -1.0):
        raise "Failed subtraction"

    elif (v1 + (0.0, 1.0)) != Vector2D(1.0, 1.0):
        raise "Failed addition with tuple"
    
    elif ((0.0, 1.0) + v1) != Vector2D(1.0, 1.0):
        raise "Failed reverse addition with tuple"

    elif ((1.0, 0.0) - v2) != Vector2D(1.0, -1.0):
        raise "Failed reverse subtraction with tuple"

    elif (-Vector2D(1.0, 1.0) != Vector2D(-1.0, -1.0)):
        raise "Failed negation"

    elif v3*2.0 != Vector2D(2.0, 2.0):
        raise "Failed scalar multiply"

    elif 2.0*v3 != Vector2D(2.0, 2.0):
        raise "Failed reverse scalar multiply"

    elif v3/2.0 != Vector2D(0.5, 0.5):
        raise "Failed scalar divide"

    iadd=Vector2D(1.0,1.0)
    iadd += v3

    if iadd != Vector2D(2.0,2.0):
        raise "failed iadd"

    isub=Vector2D(2.0,2.0)
    isub -= v3

    if isub != Vector2D(1.0,1.0):
        raise "failed isub"

    imul=Vector2D(1.0,1.0)
    imul *= 2

    if imul != Vector2D(2.0,2.0):
        raise "failed imul"

    idiv=Vector2D(2.0,2.0)
    idiv /= 2

    if idiv != Vector2D(1.0,1.0):
        raise "failed idiv"

    if float(v3) != math.sqrt(2.0):
        raise "failed length"

    if v1.dot(v2) != 0.0 or v1.dot(v3) != 1.0:
        raise "failed dot product"

    if v1.cross(v2) != 1.0 or v2.cross(v1) != -1.0:
        raise "failed cross product"



    print "Success!"
