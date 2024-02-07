import glfw
import OpenGL.GL as gl
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import glm

# Vertex Shader
VERTEX_SHADER = """
#version 330
layout(location = 0) in vec3 position;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
void main() {
    gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
}
"""

# Fragment Shader
FRAGMENT_SHADER = """
#version 330
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW can't be initialized")

# Create window
window = glfw.create_window(800, 600, "3D Simulation with Camera", None, None)

if not window:
    glfw.terminate()
    raise Exception("GLFW window can't be created")

glfw.make_context_current(window)
gl.glClearColor(0, 0.1, 0.1, 1)

# Compile shaders and program
shader = compileProgram(compileShader(VERTEX_SHADER, gl.GL_VERTEX_SHADER),
                        compileShader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER))

# Define a simple triangle
triangle = np.array([-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0], dtype=np.float32)

# Generate buffers
VBO = gl.glGenBuffers(1)
VAO = gl.glGenVertexArrays(1)
gl.glBindVertexArray(VAO)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
gl.glBufferData(gl.GL_ARRAY_BUFFER, triangle.nbytes, triangle, gl.GL_STATIC_DRAW)

# Position attribute
gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
gl.glEnableVertexAttribArray(0)

gl.glUseProgram(shader)

# Camera setup
camera_pos = glm.vec3(0, 0, 3)
camera_front = glm.vec3(0, 0, -1)
camera_up = glm.vec3(0, 1, 0)

# Main loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    # Camera/view setup
    view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)
    projection = glm.perspective(glm.radians(45), 800/600, 0.1, 100.0)

    # Pass the view and projection matrices to the shader
    view_loc = gl.glGetUniformLocation(shader, "viewMatrix")
    proj_loc = gl.glGetUniformLocation(shader, "projectionMatrix")
    gl.glUniformMatrix4fv(view_loc, 1, gl.GL_FALSE, glm.value_ptr(view))
    gl.glUniformMatrix4fv(proj_loc, 1, gl.GL_FALSE, glm.value_ptr(projection))

    gl.glBindVertexArray(VAO)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

    glfw.swap_buffers(window)

# Cleanup
glfw.terminate()
