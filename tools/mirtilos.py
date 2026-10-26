"""Cena 3D dos mirtilos caindo (hero da On Berry).

Uso:
  blender -b -P tools/mirtilos.py -- --modo desktop|mobile|still|teste --saida PASTA [--frames 180]

desktop/mobile renderizam um loop perfeito (frames PNG); still renderiza 1 quadro em 4K.
Cada objeto percorre um numero inteiro de "vaos" e de voltas por loop, entao o ultimo
quadro emenda no primeiro sem corte.
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(nome, padrao):
    return argv[argv.index(nome) + 1] if nome in argv else padrao

MODO = arg("--modo", "teste")
SAIDA = os.path.abspath(arg("--saida", "render"))
F = int(arg("--frames", "180"))
os.makedirs(SAIDA, exist_ok=True)

VERTICAL = MODO == "mobile"
if MODO == "still":
    RES = (3840, 2160); AMOSTRAS = 384
elif MODO == "mobile":
    RES = (1080, 1920); AMOSTRAS = 80
elif MODO == "desktop":
    RES = (1920, 1080); AMOSTRAS = 80
else:
    RES = (960, 540); AMOSTRAS = 48

random.seed(7 if not VERTICAL else 11)

# ---------------------------------------------------------------- cena limpa
bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.samples = AMOSTRAS
cena.cycles.use_denoising = True
cena.render.resolution_x, cena.render.resolution_y = RES
cena.render.resolution_percentage = 100
cena.render.film_transparent = False
cena.frame_start, cena.frame_end = 1, F
cena.render.fps = 30
cena.render.use_persistent_data = True
try:
    cena.view_settings.view_transform = "AgX"
    cena.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass

try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == tipo]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == tipo
                cena.cycles.device = "GPU"
                print("GPU:", tipo, [d.name for d in gpus])
                break
        except Exception as e:
            print("sem", tipo, e)
except Exception as e:
    print("GPU indisponivel", e)

mundo = bpy.data.worlds.new("mundo")
cena.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.005, 0.012, 1)
mundo.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def mix_rgba(nt):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    ins = [s for s in n.inputs if s.type == "RGBA"]
    out = [s for s in n.outputs if s.type == "RGBA"][0]
    return n, n.inputs[0], ins[0], ins[1], out


# ---------------------------------------------------------------- materiais
def mat_mirtilo():
    m = bpy.data.materials.new("mirtilo")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    info = nt.nodes.new("ShaderNodeObjectInfo")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    # mancha de cera (pruina): ruido grande, desloca por objeto
    soma = nt.nodes.new("ShaderNodeVectorMath"); soma.operation = "ADD"
    nt.links.new(coord.outputs["Object"], soma.inputs[0])
    esc = nt.nodes.new("ShaderNodeVectorMath"); esc.operation = "SCALE"
    nt.links.new(info.outputs["Random"], esc.inputs[0])
    esc.inputs["Scale"].default_value = 37.0
    nt.links.new(esc.outputs[0], soma.inputs[1])
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 1.3
    ruido.inputs["Detail"].default_value = 8.0
    ruido.inputs["Roughness"].default_value = 0.62
    nt.links.new(soma.outputs[0], ruido.inputs["Vector"])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].position = 0.30
    rampa.color_ramp.elements[1].position = 0.58
    nt.links.new(ruido.outputs["Fac"], rampa.inputs["Fac"])
    # quanto de cera cada fruta tem (algumas mais "esfregadas")
    quanto = nt.nodes.new("ShaderNodeMath"); quanto.operation = "MULTIPLY_ADD"
    nt.links.new(info.outputs["Random"], quanto.inputs[0])
    quanto.inputs[1].default_value = 0.30
    quanto.inputs[2].default_value = 0.62
    fator = nt.nodes.new("ShaderNodeMath"); fator.operation = "MULTIPLY"
    nt.links.new(rampa.outputs["Color"], fator.inputs[0])
    nt.links.new(quanto.outputs[0], fator.inputs[1])
    # cores: casca escura brilhante x cera azul-acinzentada
    mx, fac, a, b, out = mix_rgba(nt)
    a.default_value = (0.012, 0.010, 0.040, 1)
    b.default_value = (0.098, 0.112, 0.245, 1)
    nt.links.new(fator.outputs[0], fac)
    nt.links.new(out, p.inputs["Base Color"])
    rug = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(fator.outputs[0], rug.inputs["Value"])
    rug.inputs["To Min"].default_value = 0.24
    rug.inputs["To Max"].default_value = 0.62
    nt.links.new(rug.outputs[0], p.inputs["Roughness"])
    # textura fina da cera
    fino = nt.nodes.new("ShaderNodeTexNoise")
    fino.inputs["Scale"].default_value = 60.0
    fino.inputs["Detail"].default_value = 4.0
    nt.links.new(coord.outputs["Object"], fino.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    nt.links.new(fino.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    for nome, v in (("Sheen Weight", 0.35), ("Sheen Roughness", 0.4), ("Subsurface Weight", 0.06),
                    ("Specular IOR Level", 0.45)):
        if nome in p.inputs:
            p.inputs[nome].default_value = v
    if "Sheen Tint" in p.inputs:
        p.inputs["Sheen Tint"].default_value = (0.55, 0.62, 0.85, 1)
    if "Subsurface Radius" in p.inputs:
        p.inputs["Subsurface Radius"].default_value = (0.3, 0.05, 0.25)
    return m


def mat_coroa():
    m = bpy.data.materials.new("coroa")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.045, 0.030, 0.035, 1)
    p.inputs["Roughness"].default_value = 0.9
    return m


def mat_folha():
    """Folha com nervura central, nervuras laterais em relevo e borda mais escura."""
    m = bpy.data.materials.new("folha")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    L = nt.links.new
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(coord.outputs["Object"], sep.inputs[0])
    def math_(op, a=None, b=None, va=None, vb=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if a is not None: L(a, n.inputs[0])
        elif va is not None: n.inputs[0].default_value = va
        if b is not None: L(b, n.inputs[1])
        elif vb is not None: n.inputs[1].default_value = vb
        return n.outputs[0]
    ay = math_("ABSOLUTE", sep.outputs["Y"])
    # nervura central
    meio = math_("SUBTRACT", None, math_("MULTIPLY", ay, None, vb=38.0), va=1.0)
    meio = math_("MAXIMUM", meio, None, vb=0.0)
    # nervuras laterais inclinadas para a ponta
    fase = math_("SUBTRACT", sep.outputs["X"], math_("MULTIPLY", ay, None, vb=1.5))
    onda = math_("SINE", math_("MULTIPLY", fase, None, vb=26.0))
    lat = math_("POWER", math_("MAXIMUM", onda, None, vb=0.0), None, vb=14.0)
    lat = math_("MULTIPLY", lat, math_("SUBTRACT", None, math_("MULTIPLY", ay, None, vb=2.4), va=1.0))
    lat = math_("MAXIMUM", lat, None, vb=0.0)
    veias = math_("MAXIMUM", meio, math_("MULTIPLY", lat, None, vb=0.55))
    # cor: base com variacao + borda escura + veias claras
    info = nt.nodes.new("ShaderNodeObjectInfo")
    mx1, f1, a1, b1, o1 = mix_rgba(nt)
    a1.default_value = (0.018, 0.048, 0.014, 1)
    b1.default_value = (0.034, 0.068, 0.016, 1)
    L(info.outputs["Random"], f1)
    mx2, f2, a2, b2, o2 = mix_rgba(nt)
    L(o1, a2); b2.default_value = (0.010, 0.022, 0.010, 1)
    L(math_("POWER", math_("MULTIPLY", ay, None, vb=2.6), None, vb=3.0), f2)
    mx3, f3, a3, b3, o3 = mix_rgba(nt)
    L(o2, a3); b3.default_value = (0.11, 0.15, 0.045, 1)
    L(veias, f3)
    L(o3, p.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.invert = True
    L(veias, bump.inputs["Height"])
    L(bump.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.4
    for nome, v in (("Subsurface Weight", 0.12), ("Specular IOR Level", 0.42), ("Sheen Weight", 0.0)):
        if nome in p.inputs:
            p.inputs[nome].default_value = v
    return m


def mat_fundo():
    m = bpy.data.materials.new("fundo")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    saida = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    em = nt.nodes.new("ShaderNodeEmission")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    grad = nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.inputs["Scale"].default_value = (0.075, 0.075, 0.075)
    # brilho levemente deslocado para o lado das frutas
    mapa.inputs["Location"].default_value = (-0.18, -0.05, 0) if not VERTICAL else (0, -0.22, 0)
    nt.links.new(coord.outputs["Object"], mapa.inputs["Vector"])
    nt.links.new(mapa.outputs[0], grad.inputs["Vector"])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].position = 0.0
    rampa.color_ramp.elements[0].color = (0.004, 0.005, 0.012, 1)
    rampa.color_ramp.elements[1].position = 1.0
    rampa.color_ramp.elements[1].color = (0.020, 0.022, 0.060, 1)
    nt.links.new(grad.outputs["Fac"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs[0], saida.inputs["Surface"])
    return m


M_MIRTILO, M_COROA, M_FOLHA = mat_mirtilo(), mat_coroa(), mat_folha()

# ---------------------------------------------------------------- malhas
def malha_mirtilo():
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=40, radius=1.0)
    for v in bm.verts:
        v.co.z *= 0.86
        # covinha no topo onde fica a coroa
        r = math.hypot(v.co.x, v.co.y)
        if v.co.z > 0:
            k = max(0.0, 1.0 - r / 0.42)
            v.co.z -= 0.13 * (k * k * (3 - 2 * k))
        # leve irregularidade
        v.co *= 1.0 + 0.012 * math.sin(v.co.x * 5.1 + v.co.y * 3.7) * math.cos(v.co.z * 4.3)
    for f in bm.faces:
        f.smooth = True
        f.material_index = 0
    # coroa: estrela de 5 sepalas com furo
    base_z = 0.70
    pontas, vales = 0.36, 0.17
    anel_ext, anel_top = [], []
    for i in range(10):
        a = i * math.pi / 5
        rr = pontas if i % 2 == 0 else vales
        anel_ext.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), base_z)))
        # sepalas abrem e sobem um pouco
        rt = rr * (1.22 if i % 2 == 0 else 1.0)
        zt = base_z + (0.11 if i % 2 == 0 else 0.07)
        anel_top.append(bm.verts.new((rt * math.cos(a), rt * math.sin(a), zt)))
    furo_top, furo_fundo = [], []
    for i in range(10):
        a = i * math.pi / 5
        furo_top.append(bm.verts.new((0.085 * math.cos(a), 0.085 * math.sin(a), base_z + 0.05)))
        furo_fundo.append(bm.verts.new((0.06 * math.cos(a), 0.06 * math.sin(a), base_z - 0.03)))
    novas = []
    for i in range(10):
        j = (i + 1) % 10
        novas.append(bm.faces.new((anel_ext[i], anel_ext[j], anel_top[j], anel_top[i])))
        novas.append(bm.faces.new((anel_top[i], anel_top[j], furo_top[j], furo_top[i])))
        novas.append(bm.faces.new((furo_top[i], furo_top[j], furo_fundo[j], furo_fundo[i])))
    novas.append(bm.faces.new(list(reversed(furo_fundo))))
    for f in novas:
        f.smooth = True
        f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("mirtilo")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M_MIRTILO)
    me.materials.append(M_COROA)
    return me


def malha_folha():
    bm = bmesh.new()
    NX, NY = 28, 8
    grade = []
    for i in range(NX + 1):
        x = -1 + 2 * i / NX
        larg = 0.36 * (math.sin(math.pi * (x + 1) / 2) ** 0.85) + 0.004
        linha = []
        for j in range(NY + 1):
            y = (-1 + 2 * j / NY) * larg
            z = 0.16 * x * x + 0.42 * abs(y) - 0.05 * x + 0.10 * x * y
            linha.append(bm.verts.new((x, y, z)))
        grade.append(linha)
    for i in range(NX):
        for j in range(NY):
            f = bm.faces.new((grade[i][j], grade[i + 1][j], grade[i + 1][j + 1], grade[i][j + 1]))
            f.smooth = True
    me = bpy.data.meshes.new("folha")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M_FOLHA)
    return me


ME_MIRTILO, ME_FOLHA = malha_mirtilo(), malha_folha()

# ---------------------------------------------------------------- camera e luz
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 50
cam_d.sensor_width = 36
cam_d.dof.use_dof = True
cam_d.dof.focus_distance = 8.2
cam_d.dof.aperture_fstop = 2.2 if MODO != "still" else 2.4
cam = bpy.data.objects.new("cam", cam_d)
cena.collection.objects.link(cam)
cam.location = (0, -10, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
cena.camera = cam

def luz(nome, loc, energia, cor, tam, alvo=(0, 0, 0)):
    d = bpy.data.lights.new(nome, "AREA")
    d.energy, d.color, d.size = energia, cor, tam
    o = bpy.data.objects.new(nome, d)
    cena.collection.objects.link(o)
    o.location = loc
    dir_ = Vector(alvo) - Vector(loc)
    o.rotation_euler = dir_.to_track_quat("-Z", "Y").to_euler()
    return o

luz("chave", (-7, -9, 7), 2200, (1.0, 0.92, 0.84), 5)       # sol quente do sertao
luz("recorte", (8, 9, 6), 3200, (0.55, 0.66, 1.0), 4)       # contraluz fria
luz("baixo", (2, -6, -8), 380, (1.0, 0.72, 0.42), 6)        # rebote dourado

fundo_me = bpy.data.meshes.new("fundo")
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=26)
bm.to_mesh(fundo_me); bm.free()
fundo = bpy.data.objects.new("fundo", fundo_me)
fundo.data.materials.append(mat_fundo())
fundo.location = (0, 12, 0)
fundo.rotation_euler = (math.radians(90), 0, 0)
cena.collection.objects.link(fundo)

# ---------------------------------------------------------------- frutas
aspect = RES[0] / RES[1]
def meia_altura(D):
    # sensor_fit AUTO: a maior dimensao usa os 36 mm
    if aspect >= 1:
        return D * (18 / 50) / aspect
    return D * (18 / 50)

def meia_largura(D):
    if aspect >= 1:
        return D * (18 / 50)
    return D * (18 / 50) * aspect

objs = []

def nova(me, escala, D, x_rel, fase, voltas, eixo, giro0, vaos=1):
    o = bpy.data.objects.new("o", me)
    cena.collection.objects.link(o)
    o.rotation_mode = "XYZ"
    hh = meia_altura(D)
    margem = escala * 1.3 + 0.2
    objs.append(dict(o=o, s=escala, y=D - 10, x=x_rel * meia_largura(D), vao=2 * (hh + margem),
                     topo=hh + margem, ax=random.uniform(0.95, 1.05), ay=random.uniform(0.95, 1.05), az=random.uniform(0.9, 1.04), fase=fase, voltas=voltas, eixo=eixo, giro0=giro0, vaos=vaos))

def sorteia_x(peso_direita):
    if VERTICAL:
        return random.uniform(-0.95, 0.95)
    # desktop: mais frutas a direita (texto do hero fica a esquerda)
    if random.random() < peso_direita:
        return random.uniform(0.05, 1.0)
    return random.uniform(-1.0, 0.05)

camadas = [  # (quantidade, distancia min, max, escala, peso_direita)
    (3, 3.6, 4.6, 0.36, 0.75),     # primeiro plano, desfocadas e grandes
    (11, 6.8, 9.2, 0.34, 0.82),    # plano de foco
    (16, 10.5, 17.0, 0.34, 0.62),  # fundo
]
if VERTICAL:
    camadas = [(3, 3.6, 4.6, 0.36, 0), (10, 6.8, 9.2, 0.34, 0), (14, 10.5, 17.0, 0.34, 0)]

for qtd, dmin, dmax, esc, peso in camadas:
    for i in range(qtd):
        D = random.uniform(dmin, dmax)
        x = sorteia_x(peso)
        if dmax < 5:  # primeiro plano so nas bordas, para nao tapar o texto
            x = random.choice((-1, 1, 1)) * random.uniform(0.72, 1.0)
        nova(ME_MIRTILO, esc * random.uniform(0.85, 1.12), D, x,
             fase=(i + random.random()) / qtd, voltas=random.choice((0, 1, 1)),
             eixo=Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))).normalized(),
             giro0=Vector((random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28))))

for i in range(3):
    D = random.uniform(5.5, 12)
    nova(ME_FOLHA, random.uniform(0.55, 0.7), D, sorteia_x(0.7 if not VERTICAL else 0),
         fase=(i + 0.5) / 3, voltas=1,
         eixo=Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.3, 0.3))).normalized(),
         giro0=Vector((random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28))))

from mathutils import Quaternion

def atualiza(cena_, *_):
    t = (cena_.frame_current - 1 + cena_.frame_subframe) / F
    for d in objs:
        o = d["o"]
        p = (d["fase"] + t * d["vaos"]) % 1.0
        o.location = (d["x"], d["y"], d["topo"] - p * d["vao"])
        q0 = Quaternion((1, 0, 0), 0)
        q0 = q0 @ Quaternion((1, 0, 0), d["giro0"].x) @ Quaternion((0, 1, 0), d["giro0"].y)
        q = Quaternion(d["eixo"], 2 * math.pi * d["voltas"] * t) @ q0
        o.rotation_euler = q.to_euler("XYZ")
        o.scale = (d["s"] * d.get("ax", 1), d["s"] * d.get("ay", 1), d["s"] * d.get("az", 1))

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(atualiza)

cena.render.image_settings.file_format = "PNG"
cena.render.image_settings.color_depth = "8"

if MODO in ("still", "teste"):
    cena.frame_set(int(F * 0.35))
    atualiza(cena)
    cena.render.filepath = os.path.join(SAIDA, f"{MODO}.png")
    bpy.ops.render.render(write_still=True)
else:
    cena.render.filepath = os.path.join(SAIDA, "f_")
    bpy.ops.render.render(animation=True)
print("FIM", MODO)
