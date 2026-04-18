import moderngl
import numpy as np
import pygame

class BulletRenderer:
    def __init__(self, ctx, w, h):
        self.ctx = ctx
        self.w = w
        self.h = h

        # Load Bullet Texture
        try:
            bullet_surf = pygame.image.load("textures/bullet.png").convert_alpha()
            # Rotate it 90 degrees if it's horizontal by default, or handle in shader
            tex_data = pygame.image.tostring(bullet_surf, 'RGBA', 1)
            self.bullet_tex = self.ctx.texture(bullet_surf.get_size(), 4, tex_data)
        except Exception as e:
            print(f"[BulletRenderer] Failed to load bullet texture: {e}")
            self.bullet_tex = self.ctx.texture((1, 1), 4, b'\xff\xff\xff\xff')

        # Shaders for instanced bullets (Supports textures and rotations)
        self.bullet_prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec2 in_pos;
                in vec3 in_color;
                in float in_radius;
                in float in_angle;
                in float in_type;

                uniform vec2 screen_size;
                uniform vec2 cam_offset;

                out vec3 v_color;
                out vec2 v_texcoord;
                flat out int v_type;

                void main() {
                    // 2D Rotation matrix
                    // Note: adjust angle offset if bullet.png isn't pointing right by default
                    float angle = in_angle + 1.5708; // 90 degrees offset for typical vertical bullet sprites
                    float c = cos(angle);
                    float s = sin(angle);
                    mat2 rot = mat2(c, s, -s, c);
                    
                    vec2 pos = (in_pos - cam_offset + (rot * in_vert) * in_radius * 2.0);
                    gl_Position = vec4((pos / screen_size) * 2.0 - 1.0, 0.0, 1.0);
                    gl_Position.y *= -1.0; 
                    
                    v_color = in_color;
                    v_texcoord = in_vert + 0.5; 
                    v_type = int(in_type);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D BulletTex;
                in vec3 v_color;
                in vec2 v_texcoord;
                flat in int v_type;
                out vec4 f_color;
                
                void main() {
                    if (v_type == 1) { // Textured Bullet
                        vec4 tex_color = texture(BulletTex, v_texcoord);
                        if (tex_color.a < 0.1) discard;
                        f_color = tex_color; // Keep original PNG colors or multiply by v_color for tinting
                    } else { // Procedural High-Quality Circle
                        float dist = length(v_texcoord - 0.5);
                        if (dist > 0.5) discard;
                        float alpha = smoothstep(0.5, 0.48, dist);
                        f_color = vec4(v_color, alpha);
                    }
                }
            '''
        )
        self.bullet_prog['screen_size'].value = (w, h)

        vertices = np.array([-0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0.5, 0.5], dtype='f4')
        self.vbo_geom = self.ctx.buffer(vertices)

        # Buffer for: pos(2f), color(3f), radius(1f), angle(1f), type(1i)
        MAX_BULLETS = 10_000
        FLOATS_PER_BULLET = 8
        self.instance_vbo = self.ctx.buffer(reserve=MAX_BULLETS * FLOATS_PER_BULLET * 4) 
        self.vao = self.ctx.vertex_array(
            self.bullet_prog,
            [
                (self.vbo_geom, '2f', 'in_vert'),
                (self.instance_vbo, '2f 3f 1f 1f 1f /i', 'in_pos', 'in_color', 'in_radius', 'in_angle', 'in_type')
            ]
        )

    def draw(self, bullet_data_np, cam_offset):
        if len(bullet_data_np) == 0:
            return
            
        # We now receive a ready-to-go numpy array of shape (N, 8) from ProjectileManager
        # Size in bytes is len * 8 floats * 4 bytes = len * 32
        data_bytes = bullet_data_np.tobytes()
        
        if len(data_bytes) > self.instance_vbo.size:
            self.instance_vbo.orphan(len(data_bytes))
            
        self.instance_vbo.write(data_bytes)
        self.bullet_prog['cam_offset'].value = cam_offset
        self.bullet_tex.use(1)
        self.bullet_prog['BulletTex'].value = 1
        self.vao.render(mode=moderngl.TRIANGLE_STRIP, instances=len(bullet_data_np))

class UIRenderer:
    """Renderer for the standard Pygame Surface (UI, Player, Map)."""
    def __init__(self, ctx, w, h):
        self.ctx = ctx
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D Texture;
                in vec2 v_texcoord;
                out vec4 f_color;
                void main() {
                    // Pygame buffer view is BGRA, swizzle it mathematically to RGBA
                    f_color = texture(Texture, v_texcoord).bgra;
                    // Discard transparent pixels to allow layers below to show
                    if (f_color.a < 0.1) discard;
                }
            '''
        )
        # Full screen quad NDC - Adjusted UV mapping for raw un-flipped pygame buffer
        vertices = np.array([
            -1.0, -1.0, 0.0, 1.0, # Bottom Left NDC -> Bottom Left Tex (y=1)
             1.0, -1.0, 1.0, 1.0, # Bottom Right NDC -> Bottom Right Tex (y=1)
            -1.0,  1.0, 0.0, 0.0, # Top Left NDC -> Top Left Tex (y=0)
             1.0,  1.0, 1.0, 0.0, # Top Right NDC -> Top Right Tex (y=0)
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '2f 2f', 'in_vert', 'in_texcoord')])
        self.texture = None
        # PBO for fast asynchronous texture uploads without CPU allocation bottlenecks
        self.pbo = self.ctx.buffer(reserve=w * h * 4)

    def draw(self, surface):
        view = surface.get_view('1')
        
        # Dynamic PBO resizing in case surface size changes
        expected_size = surface.get_width() * surface.get_height() * 4
        if self.pbo.size != expected_size:
            self.pbo.orphan(expected_size)
            
        self.pbo.write(view)
        
        if not self.texture or self.texture.size != surface.get_size():
            if self.texture:
                self.texture.release()
            self.texture = self.ctx.texture(surface.get_size(), 4)
            
        self.texture.write(self.pbo)
            
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

class MasterRenderer:
    """Coordinates the Hybrid drawing process."""
    def __init__(self, w, h):
        self.ctx = moderngl.create_context()
        # Enable alpha blending for transparency
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        self.bullet_renderer = BulletRenderer(self.ctx, w, h)
        self.ui_renderer = UIRenderer(self.ctx, w, h)
        
    def render(self, display_surface, bullet_data_np, cam_offset):
        # Clear with the background color of your choice (Black here)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # 1. Draw the Pygame surface first (contains map, characters, UI)
        self.ui_renderer.draw(display_surface)
        
        # 2. Draw bullets ON TOP of the game world natively
        self.bullet_renderer.draw(bullet_data_np, cam_offset)
