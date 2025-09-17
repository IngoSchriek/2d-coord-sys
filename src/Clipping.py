import math

def ppc_to_wc(u, v, window):
    xr = (u - 0.5) * window.width()
    yr = (v - 0.5) * window.height()
    
    cx, cy = window.center()
    theta = math.radians(window.angle)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    
    xw = cos_t * xr - sin_t * yr + cx
    yw = sin_t * xr + cos_t * yr + cy
    
    return (xw, yw)

def wc_to_ppc(point, window):
    xw, yw = point
    cx, cy = window.center()
    theta = math.radians(window.angle)
    cos_t, sin_t = math.cos(-theta), math.sin(-theta)
    xr = cos_t * (xw - cx) - sin_t * (yw - cy)
    yr = sin_t * (xw - cx) + cos_t * (yw - cy)
    u = (xr / window.width()) + 0.5
    v = (yr / window.height()) + 0.5
    return u, v

def clip_point(p, window):
    u, v = wc_to_ppc(p, window)
    return (0.0 <= u <= 1.0) and (0.0 <= v <= 1.0)

INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_outcode_ppc(u, v):
    code = INSIDE
    if u < 0.0: 
        code |= LEFT
    elif u > 1.0: 
        code |= RIGHT
    if v < 0.0: 
        code |= BOTTOM
    elif v > 1.0: 
        code |= TOP
    return code

# cohen-sutherland
def clip_line_cs(p1, p2, window):
    u1, v1 = wc_to_ppc(p1, window)
    u2, v2 = wc_to_ppc(p2, window)
    
    out1 = compute_outcode_ppc(u1, v1)
    out2 = compute_outcode_ppc(u2, v2)
    
    while True:
        if not (out1 | out2):
            result_p1 = ppc_to_wc(u1, v1, window)
            result_p2 = ppc_to_wc(u2, v2, window)
            return [result_p1, result_p2]
        elif out1 & out2:
            return None
        else:
            out = out1 if out1 else out2
            
            if out & TOP:
                if v2 == v1:
                    return None
                u = u1 + (u2 - u1) * (1.0 - v1) / (v2 - v1)
                v = 1.0
            elif out & BOTTOM:
                if v2 == v1:
                    return None
                u = u1 + (u2 - u1) * (0.0 - v1) / (v2 - v1)
                v = 0.0
            elif out & RIGHT:
                if u2 == u1:
                    return None
                v = v1 + (v2 - v1) * (1.0 - u1) / (u2 - u1)
                u = 1.0
            elif out & LEFT:
                if u2 == u1:
                    return None
                v = v1 + (v2 - v1) * (0.0 - u1) / (u2 - u1)
                u = 0.0
            
            if out == out1:
                u1, v1 = u, v
                out1 = compute_outcode_ppc(u1, v1)
            else:
                u2, v2 = u, v
                out2 = compute_outcode_ppc(u2, v2)

# liang-barsky
def clip_line_lb(p1, p2, window):
    u1, v1 = wc_to_ppc(p1, window)
    u2, v2 = wc_to_ppc(p2, window)
    
    du = u2 - u1
    dv = v2 - v1
    
    p = [-du, du, -dv, dv]
    q = [u1 - 0.0, 1.0 - u1, v1 - 0.0, 1.0 - v1]
    
    t1, t2 = 0.0, 1.0
    
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                t1 = max(t1, t)
            else:
                t2 = min(t2, t)
    
    if t1 > t2:
        return None
    
    u1_clip = u1 + t1 * du
    v1_clip = v1 + t1 * dv
    u2_clip = u1 + t2 * du
    v2_clip = v1 + t2 * dv
    
    result_p1 = ppc_to_wc(u1_clip, v1_clip, window)
    result_p2 = ppc_to_wc(u2_clip, v2_clip, window)
    return [result_p1, result_p2]

# sutehrland-hogdman
def clip_polygon_sh(polygon, window):
    if not polygon:
        return []
    
    ppc_polygon = [wc_to_ppc(p, window) for p in polygon]
    
    def inside_ppc(p, edge):
        u, v = p
        if edge == "LEFT": 
            return u >= 0.0
        if edge == "RIGHT": 
            return u <= 1.0
        if edge == "BOTTOM": 
            return v >= 0.0
        if edge == "TOP": 
            return v <= 1.0
    
    def intersection_ppc(p1, p2, edge):
        u1, v1 = p1
        u2, v2 = p2
        
        if edge in ["LEFT", "RIGHT"] and u2 == u1:
            return None
        if edge in ["BOTTOM", "TOP"] and v2 == v1:
            return None
            
        if edge == "LEFT":
            return (0.0, v1 + (v2 - v1) * (0.0 - u1) / (u2 - u1))
        elif edge == "RIGHT":
            return (1.0, v1 + (v2 - v1) * (1.0 - u1) / (u2 - u1))
        elif edge == "BOTTOM":
            return (u1 + (u2 - u1) * (0.0 - v1) / (v2 - v1), 0.0)
        elif edge == "TOP":
            return (u1 + (u2 - u1) * (1.0 - v1) / (v2 - v1), 1.0)
    
    def clip_edge_ppc(vertices, edge):
        output = []
        if not vertices:
            return output
        
        prev = vertices[-1]
        for curr in vertices:
            if inside_ppc(curr, edge):
                if not inside_ppc(prev, edge):
                    intersect = intersection_ppc(prev, curr, edge)
                    if intersect:
                        output.append(intersect)
                output.append(curr)
            elif inside_ppc(prev, edge):
                intersect = intersection_ppc(prev, curr, edge)
                if intersect:
                    output.append(intersect)
            prev = curr
        return output
    
    clipped_ppc = ppc_polygon[:]
    for edge in ["LEFT", "RIGHT", "BOTTOM", "TOP"]:
        clipped_ppc = clip_edge_ppc(clipped_ppc, edge)
        if not clipped_ppc:
            break
    
    if clipped_ppc:
        return [ppc_to_wc(u, v, window) for u, v in clipped_ppc]
    else:
        return []