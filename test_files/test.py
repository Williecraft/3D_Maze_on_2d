from PIL import Image, ImageDraw

MIN = 2
MAX = 30

img = Image.new("RGB", ((MAX+2)*10, 100), color="white")
draw = ImageDraw.Draw(img)


sep = 512/(MAX-MIN)
w = 2
l = 0
for i in range(MIN, MAX+1):
    R = min(round(l), 255)
    G = min(512-round(l), 255)
    draw.rectangle((i*10+2, 10, (i+1)*10-2, 90), fill= (R, G, 0))
    draw.rectangle((i*10+2+w, 10+w, (i+1)*10-2-w, 90-w), fill="black")
    l += sep
    
img.show()