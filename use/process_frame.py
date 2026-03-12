import cv2
from path_searching import astar


CONF_THRESHOLD = 0.5

def process_ninja_frame(frame, model):
    results = model(frame)[0]
    annotated_frame = results.plot(conf=True)
    fruits = []
    bombs = []

    for box in results.boxes:
        # xywh נותן לנו מרכז (cx, cy) ורוחב/גובה (w, h)
        conf = float(box.conf[0])
        if conf < CONF_THRESHOLD:
            continue

        cx, cy, w, h = box.xywh[0].tolist()
        label = results.names[int(box.cls[0])]
        
        if label == 'Fruit':
            # נגדיר קו חיתוך אופקי שעובר דרך הפרי (קצת מעבר לשוליים שלו)
            entry = (int(cx - w/2 - 10), int(cy))
            exit = (int(cx + w/2 + 10), int(cy))
            fruits.append({'entry': entry, 'exit': exit, 'cx': cx})
        elif label == 'Bomb':
            bombs.append((int(cx), int(cy)))

    # מיון פירות משמאל לימין
    fruits.sort(key=lambda f: f['cx'])

    full_combo_path = []
    
    for i in range(len(fruits)):
        # 1. הוספת קטע ה-A* מהפרי הקודם לכניסה של הפרי הנוכחי
        if i > 0:
            last_exit = fruits[i-1]['exit']
            bridge = astar(last_exit, fruits[i]['entry'], bombs, map_size=frame.shape[1])
            full_combo_path.extend(bridge)
        else:
            # אם זה הפרי הראשון, פשוט נתחיל מהכניסה שלו
            full_combo_path.append(fruits[i]['entry'])

        # 2. הוספת קטע החיתוך הישיר (כניסה -> יציאה)
        # זה הקטע שבו הסכין עוברת בתוך הפרי
        full_combo_path.append(fruits[i]['exit'])

    # ציור המסלול
    if len(full_combo_path) > 1:
        for i in range(len(full_combo_path) - 1):
            cv2.line(annotated_frame, full_combo_path[i], full_combo_path[i+1], (0, 255, 0), 3)

    return annotated_frame, full_combo_path