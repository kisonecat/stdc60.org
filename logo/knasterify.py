#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p "python3.withPackages(ps: [ ps.svgpathtools ])"

import argparse
import math
import xml.etree.ElementTree as ET
from svgpathtools import parse_path

def cantor_midpoints(n):
    """Generates the midpoints of the intervals in the n-th stage Cantor set."""
    intervals = [(0.0, 1.0)]
    for _ in range(n):
        new_intervals = []
        for a, b in intervals:
            w = b - a
            new_intervals.append((a, a + w / 3))
            new_intervals.append((b - w / 3, b))
        intervals = new_intervals
    return [(a + b) / 2 for a, b in intervals]

def top_partner(i, n):
    """Connections at the end of the path (t=1)."""
    return (2**n) - 1 - i

def bottom_partner(i, n):
    """Connections at the start of the path (t=0)."""
    if n == 0: return 0
    half = 2**(n - 1)
    if i < half:
        return half - 1 - i
    else:
        return 3 * half - 1 - i

def generate_cap(A, B, center_normal, forward_tangent):
    """Generates a semicircular polyline connecting point A to B."""
    if abs(A - B) < 1e-6:
        return []
        
    center = (A + B) / 2
    u = A - center
    R = abs(u)
    if R < 1e-6:
        return []

    # Choose the normal direction that bulges "forward"
    v_cand = u * 1j
    dot = v_cand.real * forward_tangent.real + v_cand.imag * forward_tangent.imag
    if dot < 0:
        v_cand = u * -1j
    v = v_cand * (R / abs(v_cand))

    cap_points = []
    steps = max(10, int(R))
    for i in range(1, steps):
        theta = math.pi * i / steps
        cap_points.append(center + u * math.cos(theta) + v * math.sin(theta))
    return cap_points

def generate_buckethandle(path_obj, N, W):
    """Maps the N-th stage Knaster continuum onto an svgpathtools Path."""
    if N == 0:
        return path_obj.d()

    all_d_strings = []

    for subpath in path_obj.continuous_subpaths():
        L = subpath.length()
        if L < 1e-6: continue

        # Sample the subpath uniformly by arc length
        num_samples = max(int(L / 2), 50) 
        t_vals = [subpath.ilength(L * i / (num_samples - 1)) for i in range(num_samples)]
        points = [subpath.point(t) for t in t_vals]

        # Calculate smooth tangents and normals via finite differences
        tangents = []
        for i in range(num_samples):
            if i == 0:
                t = points[1] - points[0]
            elif i == num_samples - 1:
                t = points[-1] - points[-2]
            else:
                t = points[i+1] - points[i-1]
            if abs(t) == 0: t = 1 + 0j
            tangents.append(t / abs(t))

        normals = [t * 1j for t in tangents] 

        # Generate the parallel continuous strands based on the Cantor set
        strands = []
        cantor = cantor_midpoints(N)
        for c in cantor:
            d = (c - 0.5) * W
            strand = [points[k] + d * normals[k] for k in range(num_samples)]
            strands.append(strand)

        # Graph traversal to link strands into continuous topological loops
        visited_strands = [False] * (2**N)

        for start_i in range(2**N):
            if visited_strands[start_i]: continue

            loop_points = []
            curr_i = start_i
            going_up = True 

            while not visited_strands[curr_i]:
                visited_strands[curr_i] = True

                if going_up:
                    loop_points.extend(strands[curr_i])
                    nxt_i = top_partner(curr_i, N)
                    if nxt_i != curr_i:
                        A = strands[curr_i][-1]
                        B = strands[nxt_i][-1]
                        cap = generate_cap(A, B, normals[-1], tangents[-1])
                        loop_points.extend(cap)
                    curr_i = nxt_i
                    going_up = False
                else:
                    loop_points.extend(reversed(strands[curr_i]))
                    nxt_i = bottom_partner(curr_i, N)
                    if nxt_i != curr_i:
                        A = strands[curr_i][0]
                        B = strands[nxt_i][0]
                        cap = generate_cap(A, B, normals[0], -tangents[0])
                        loop_points.extend(cap)
                    curr_i = nxt_i
                    going_up = True

            # Format the points into an SVG d-string
            d_str = "M " + " L ".join(f"{p.real:.3f},{p.imag:.3f}" for p in loop_points)
            
            # Close the loop if the ends meet
            if abs(loop_points[0] - loop_points[-1]) < 1e-3:
                d_str += " Z"
                
            all_d_strings.append(d_str)

    return " ".join(all_d_strings)

def process_svg(input_file, output_file, N, W):
    """Parses SVG, modifies all path elements, and saves the output."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(input_file)
    root = tree.getroot()

    for elem in root.iter():
        # Strip namespace for tag checking
        tag = elem.tag.split('}')[-1] 
        
        if tag == 'path':
            d_attr = elem.get('d')
            if d_attr:
                try:
                    path_obj = parse_path(d_attr)
                    new_d = generate_buckethandle(path_obj, N, W)
                    elem.set('d', new_d)
                    
                    # Ensure lines are visible and empty inside
                    elem.set('fill', 'none')
                    if not elem.get('stroke'):
                        elem.set('stroke', 'black')
                except Exception as e:
                    print(f"Skipping a path due to error: {e}")

    tree.write(output_file)
    print(f"Successfully generated Stage {N} Buckethandle to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map a Knaster continuum onto an SVG path.")
    parser.add_argument("input", help="Input SVG file path")
    parser.add_argument("output", help="Output SVG file path")
    parser.add_argument("-n", "--stage", type=int, default=3, help="Stage of the continuum (e.g. 3)")
    parser.add_argument("-w", "--width", type=float, default=20.0, help="Total width of the buckethandle ribbon")
    
    args = parser.parse_args()
    process_svg(args.input, args.output, args.stage, args.width)
