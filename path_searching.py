import heapq
import math

from matplotlib.pyplot import step
# --- פונקציית עזר: חישוב מרחק (Heuristic) ---
# מחשבת את המרחק בין שתי נקודות לפי שיטת מרחק מנהטן (Manhattan Distance).
# משתמשים בזה במקום חישוב מרחק מדויק (עם שורש) כי זה הרבה יותר מהיר למחשב.
def _distance(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

# --- פונקציית עזר: הימנעות מפצצות ---
# בודקת אם הנקודה שבה אנחנו רוצים לעבור נמצאת בתוך "רדיוס הסכנה" של פצצה.
def point_inside_bomb(x, y, bombs, threshold=100):
    for bx, by in bombs:
        if ((x - bx)**2 + (y - by)**2)**0.5 < threshold:
            return True
    return False

def astar(start, end, bombs, map_size=2000, step=5):
    # שמונה כיווני תנועה אפשריים (ימינה, שמאלה, למעלה, למטה ואלכסונים)
    directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # קבוצה של נקודות שכבר בדקנו
    close_set = set()
    # מילון ששומר מאיפה הגענו לכל נקודה 
    came_from = {}
    # העלות של המסלול מההתחלה ועד לנקודה הנוכחית  
    gscore = {start: 0}
    # ציון הכולל של הנקודה (מרחק שעברנו + מרחק משוער ליעד)
    fscore = {start: _distance(start, end)}

    # תור עדיפויות שדואג שתמיד נבדוק קודם את הנקודות עם הציון הטוב ביותר        
    open_heap = []
    heapq.heappush(open_heap, (fscore[start], start))

    while open_heap:
        # שולפים את הנקודה בעלת הציון הכי טוב (הכי קרובה ליעד)
        current = heapq.heappop(open_heap)[1]

        # תנאי עצירה: אם התקרבנו ליעד בטווח של "צעד" אחד, סיימנו את החיפוש
        if _distance(current, end) < step: # הגענו מספיק קרוב ליעד
            path = []
            # שחזור המסלול מהסוף להתחלה בעזרת המילון
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        # מסמנים את הנקודה הנוכחית כ"נבדקה"
        close_set.add(current)

        # עוברים על כל הכיוונים האפשריים סביב הנקודה
        for dx, dy in directions:
            neighbor = (current[0] + dx * step, current[1] + dy * step)
            
            # --- בדיקות ---
            # האם יצאנו מגבולות המסך
            # האם כבר היינו בנקודה הזו
            # האם הנקודה הזו חותכת פצצה
            if (neighbor[0] < 0 or neighbor[0] >= map_size or 
                neighbor[1] < 0 or neighbor[1] >= map_size or 
                neighbor in close_set or 
                point_inside_bomb(neighbor[0], neighbor[1], bombs)):
                continue # אם אחד מהתנאים מתקיים, דלג לנקודה הבאה
            if dx != 0 and dy != 0:
                # אלכסון
                move_cost = step * math.sqrt(2)
            else:
                # ישר
                move_cost = step

            # חישוב עלות הנוכחית של המסלול דרך הנקודה השכנה
            tentative_gscore = gscore[current] + move_cost

            # אם מצאנו דרך מהירה יותר להגיע לנקודה הזו, או שזו פעם ראשונה שאנחנו רואים אותה
            if neighbor not in gscore or tentative_gscore < gscore.get(neighbor, float('inf')):
                # שומרים את הנתונים המעודכנים
                came_from[neighbor] = current
                gscore[neighbor] = tentative_gscore
                fscore[neighbor] = tentative_gscore + _distance(neighbor, end)
                heapq.heappush(open_heap, (fscore[neighbor], neighbor))

    # אם התור התרוקן ולא הגענו ליעד (למשל, כי פצצות חוסמות לחלוטין את הדרך)
    return []

