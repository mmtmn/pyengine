import pyglet
from pyglet.gl import *
import numpy as np
from pyglet.window import key
from pyrr import Matrix44, Vector3
import ctypes

# Window setup
window = pyglet.window.Window(800, 600, "3D Simulation with Camera", resizable=True)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

# Shader setup
vertex_shader_source = """
#version 330
layout(location = 0) in vec3 position;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 modelMatrix;
void main() {
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
}
"""

fragment_shader_source = """
#version 330
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

# Compile shaders and create a program
vertex_shader = GLuint(glCreateShader(GL_VERTEX_SHADER))
source = ctypes.create_string_buffer(vertex_shader_source.encode())
length = ctypes.c_int(-1)
glShaderSource(vertex_shader, 1, ctypes.cast(ctypes.pointer(ctypes.pointer(source)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), ctypes.byref(length))
glCompileShader(vertex_shader)

fragment_shader = GLuint(glCreateShader(GL_FRAGMENT_SHADER))
source = ctypes.create_string_buffer(fragment_shader_source.encode())
length = ctypes.c_int(-1)
glShaderSource(fragment_shader, 1, ctypes.cast(ctypes.pointer(ctypes.pointer(source)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), ctypes.byref(length))
glCompileShader(fragment_shader)

shader_program = glCreateProgram()
glAttachShader(shader_program, vertex_shader)
glAttachShader(shader_program, fragment_shader)
glLinkProgram(shader_program)
glUseProgram(shader_program)

# Cube vertices
cube = np.array([
    # Front face
    -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
    -0.5, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5,  0.5,

    # Back face
    -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5, -0.5,
    -0.5, -0.5, -0.5,  0.5,  0.5, -0.5,  0.5, -0.5, -0.5,

    # Top face
    -0.5,  0.5, -0.5, -0.5,  0.5,  0.5,  0.5,  0.5,  0.5,
    -0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,  0.5, -0.5,

    # Bottom face
    -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5,  0.5,
    -0.5, -0.5, -0.5,  0.5, -0.5,  0.5, -0.5, -0.5,  0.5,

    # Right face
     0.5, -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,
     0.5, -0.5, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5,

    # Left face
    -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,
    -0.5, -0.5, -0.5, -0.5,  0.5,  0.5, -0.5,  0.5, -0.5
], dtype=np.float32)

# Vertex Array Object
VAO = GLuint()
glGenVertexArrays(1, ctypes.byref(VAO))
glBindVertexArray(VAO)

# Vertex Buffer Object
VBO = GLuint()
glGenBuffers(1, ctypes.byref(VBO))
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, cube.nbytes, cube.ctypes.data, GL_STATIC_DRAW)

# Vertex attribute pointers
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

# Camera setup
camera_pos = Vector3([0, 0, 3])
camera_front = Vector3([0, 0, -1])
camera_up = Vector3([0, 1, 0])

# Rotation angle variables
x_rotate = 0
y_rotate = 0
z_rotate = 0

@window.event
def on_draw():
    global x_rotate, y_rotate, z_rotate

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Camera/view setup
    view = Matrix44.look_at(camera_pos, camera_pos + camera_front, camera_up)
    projection = Matrix44.perspective_projection(45.0, window.width / window.height, 0.1, 100.0)

    # Apply rotation
    model = Matrix44.from_x_rotation(np.radians(x_rotate)) * \
            Matrix44.from_y_rotation(np.radians(y_rotate)) * \
            Matrix44.from_z_rotation(np.radians(z_rotate))

    # Pass matrices to shader
    view_loc = glGetUniformLocation(shader_program, b"viewMatrix")
    proj_loc = glGetUniformLocation(shader_program, b"projectionMatrix")
    model_loc = glGetUniformLocation(shader_program, b"modelMatrix")

    view_array = np.array(view, dtype=np.float32)
    proj_array = np.array(projection, dtype=np.float32)
    model_array = np.array(model, dtype=np.float32)

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, proj_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_array.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)


# Key state dictionary
keys = key.KeyStateHandler()
window.push_handlers(keys)

def update(dt):
    global x_rotate, y_rotate, z_rotate
    if keys[key.UP]:
        x_rotate += 1
    if keys[key.DOWN]:
        x_rotate -= 1
    if keys[key.RIGHT]:
        y_rotate += 1
    if keys[key.LEFT]:
        y_rotate -= 1
    if keys[key.PAGEUP]:
        z_rotate += 1
    if keys[key.PAGEDOWN]:
        z_rotate -= 1

pyglet.clock.schedule_interval(update, 1/60.0)  # 60 times per second

@window.event
def on_draw():
    global x_rotate, y_rotate, z_rotate

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

pyglet.app.run()
