import wave as wav
import struct
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import cv2
from math import sin, cos, pi, sqrt
import numpy as np
name = input("File: ")
bars = 1024
freq = 3000
fps = 15
dv = 80
lns = False
closed = False
started = False
def fft(n):
    return [(j[0] / dv, j[1] / dv) for j in fft1([(i, 0) for i in n], True)]
def fft1(n, h=False):
    if len(n) == 1:
        return n
    r = fft1([n[i] for i in range(0, len(n), 2)])
    r2 = fft1([n[i] for i in range(1, len(n), 2)])
    rl = []
    for k in range(len(n)):
        if h and k >= len(n) // 2:
            break
        rl.append((r[k % len(r)][0] + (cos(2 * pi * k / len(n)) * r2[k % len(r2)][0] + sin(2 * pi * k / len(n)) * r2[k % len(r2)][1]), r[k % len(r)][1] + (cos(2 * pi * k / len(n)) * r2[k % len(r2)][1] - sin(2 * pi * k / len(n)) * r2[k % len(r2)][0])))
    return rl
def onclose():
    global closed
    closed = True
def onstart():
    global started
    started = True
def getcol(n):
    if n < 1/3:
        r = 1
        g = n * 3
        b = 0
    elif n < 2/3:
        r = 2 - n * 3
        g = 1
        b = 0
    else:
        r = 0
        g = 1
        b = n * 3 - 2
    c = int(r * 255) * 65536 + int(g * 255) * 256 + int(b * 255)
    return "#" + "".join(["0123456789ABCDEF"[(c % (16 ** (6 - i))) // (16 ** (5 - i))] for i in range(6)])
with wav.open("sounds\\" + name + ".wav", 'rb') as f:
    for _ in range(1):
        n = [i / 32768 for i in struct.unpack(str(f.getnframes() * f.getnchannels()) + "h", f.readframes(f.getnframes()))]
        n = [sum(n[i:i + f.getnchannels()]) / f.getnchannels() for i in range(0, len(n) - 1, f.getnchannels())]
        skip = int(f.getframerate() // (freq * 2))
        nfps = int(f.getframerate() // fps)
        plt.gca().set_xlim(0, 1)
        plt.gca().set_ylim(0, 1)
        plt.gca().xaxis.set_visible(False)
        plt.gca().yaxis.set_visible(False)
        plt.ion()
        plt.connect('close_event', (lambda _: onclose()))
        plt.connect('button_press_event', (lambda _: onstart()))
        plt.plot([0, 1], [0, 0], color="#000000")
        plt.show()
        while not (started or closed):
            plt.pause(0.05)
        if closed:
            break
        out = False
        pxls = None
        for i in range(0, len(n) - (bars * skip) + 1, nfps):
            if closed:
                break
            ft1 = fft(n[i:i + bars * skip:skip])
            ft = [sqrt(j[0] ** 2 + j[1] ** 2) for j in ft1]
            if lns:
                lns.remove()
            r = np.linspace(0, 1, len(ft))
            pts = np.concatenate([r.reshape((len(ft), 1, 1)), np.array([[[j]] for j in ft])], axis=2)
            lns = LineCollection(np.concatenate([[[[k, 0]] for k in r], pts], axis=1), cmap=LinearSegmentedColormap.from_list("custom", [getcol(j / len(ft)) for j in range(len(ft))], 256))
            lns.set_array(r) # color the segments
            plt.gca().add_collection(lns)
            plt.pause(0.01)
            plt.savefig("tempfile.png")
            img = cv2.imread("tempfile.png")
            if not out:
                pxls = (img.shape[1], img.shape[0])
                out = cv2.VideoWriter("sounds\\" + name + "a.avi", cv2.VideoWriter_fourcc(*'MJPG'), fps, pxls)
            out.write(img)
        if out:
            out.release()