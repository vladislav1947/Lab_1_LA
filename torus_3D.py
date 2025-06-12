import tkinter as tk
import numpy as np
import math

# const
WIDTH, HEIGHT = 1400, 800
CURRENT_SCALE = 100
ALPHA = 3.0
BETA = 1.0

scale = CURRENT_SCALE
angle_x, angle_y = 0.0, 0.0
mouse_drag = False
prev_mouse = None

def do_rotation_matrix(angle_x, angle_y):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)

    rot_x = np.array([
        [1, 0, 0],
        [0, cos_x, -sin_x],
        [0, sin_x, cos_x]
    ])

    rot_y = np.array([
        [cos_y, 0, sin_y],
        [0, 1, 0],
        [-sin_y, 0, cos_y]
    ])

    return rot_y @ rot_x

def world_to_screen_coordinates(point, rotation_matrix, scale, center_x, center_y):
    rotated = rotation_matrix @ point
    x, y, z = rotated
    z += 6
    k = scale / z
    x_pro = center_x + x * k
    y_pro = center_y - y * k
    return (x_pro, y_pro), rotated

def generate_torus(alpha, beta, u_steps, v_steps):
    points = []
    for i in range(u_steps):
        u = 2 * math.pi * i / u_steps
        for j in range(v_steps):
            v = 2 * math.pi * j / v_steps
            x = (alpha + beta * math.cos(v)) * math.cos(u)
            y = (alpha + beta * math.cos(v)) * math.sin(u)
            z = beta * math.sin(v)
            points.append((x, y, z))
    return points, u_steps, v_steps

def draw_tor():
    canvas.delete("all")

    u_steps = int(scale / 5)
    v_steps = int(scale / 5)

    points, u_count, v_count = generate_torus(ALPHA, BETA, u_steps, v_steps)

    rotation_matrix = do_rotation_matrix(angle_x, angle_y)

    projected = []
    rotated = []

    for p in points:
        screen_point, rotated_point = world_to_screen_coordinates(
            np.array(p), rotation_matrix, scale, WIDTH // 2, HEIGHT // 2
        )
        projected.append(screen_point)
        rotated.append(rotated_point)

    triangles = []

    for i in range(u_count):
        for j in range(v_count):
            index = i * v_count + j
            next_i = (i + 1) % u_count
            next_j = (j + 1) % v_count

            a = projected[index]
            b = projected[next_i * v_count + j]
            c = projected[next_i * v_count + next_j]
            d = projected[i * v_count + next_j]

            pa = rotated[index]
            pb = rotated[next_i * v_count + j]
            pc = rotated[next_i * v_count + next_j]
            pd = rotated[i * v_count + next_j]

            triangles.append(((a, b, c), (pa, pb, pc)))
            triangles.append(((a, c, d), (pa, pc, pd)))

    def avg_z(rotated_triangle):
        return sum(p[2] for p in rotated_triangle) / 3

    triangles.sort(key=lambda tri: avg_z(tri[1]), reverse=True)

    light_dir = np.array([-1, 1, -2])

    for screen_triangle, world_triangle in triangles:
        pa, pb, pc = world_triangle
        normal = np.cross(pb - pa, pc - pa)

        normal = normal / np.linalg.norm(normal)
        light_norm = light_dir / np.linalg.norm(light_dir)

        brightness = np.dot(normal, light_norm)
        brightness = max(0.3, min(1, brightness))

        gray = int(255 * brightness)
        color = f'#{gray:02x}{gray:02x}{gray:02x}'

        canvas.create_polygon(screen_triangle, fill=color, outline=color)

def increase_scale():
    global scale
    scale *= 1.5
    draw_tor()

def decrease_scale():
    global scale
    scale /= 1.5
    draw_tor()

def on_mouse_down(event):
    global mouse_drag, prev_mouse
    mouse_drag = True
    prev_mouse = (event.x, event.y)

def on_mouse_move(event):
    global mouse_drag, angle_x, angle_y, prev_mouse
    if mouse_drag:
        dx = event.x - prev_mouse[0]
        dy = event.y - prev_mouse[1]
        angle_y += dx * 0.01
        angle_x += dy * 0.01
        prev_mouse = (event.x, event.y)
        draw_tor()

def on_mouse_up(event):
    global mouse_drag
    mouse_drag = False

# Interface
root = tk.Tk()
root.geometry(f"{WIDTH}x{HEIGHT}")
root.title("3D Тор")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
canvas.pack()

frame = tk.Frame(root)
frame.place(x=10, y=10)
tk.Button(frame, text="Увеличить", command=increase_scale).grid(row=0, column=0)
tk.Button(frame, text="Уменьшить", command=decrease_scale).grid(row=0, column=1)

canvas.bind("<Button-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

draw_tor()
root.mainloop()