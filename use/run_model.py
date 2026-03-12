import os
from ultralytics import YOLO
import cv2
from process_frame import process_ninja_frame
import keyboard
import time
import pyautogui
import bettercam
import threading

# טעינת המודל
model = YOLO('my_model.pt')

# הגדרות בטיחות ומהירות עבור pyautogui
pyautogui.PAUSE = 0.00000001
pyautogui.FAILSAFE = True

# חישובי מידות המסך והתאמה לרזולוציות שונות
SCREEN_W, SCREEN_H = pyautogui.size()
GAME_LEFT = int((553 / 1920) * SCREEN_W)
GAME_TOP = int((200 / 1080) * SCREEN_H)
GAME_RIGHT = int((1352 / 1920) * SCREEN_W)
GAME_BOTTOM = int((780 / 1080) * SCREEN_H)

# הגדרת אזור הצילום עבור bettercam
REGION = (GAME_LEFT, GAME_TOP, GAME_RIGHT, GAME_BOTTOM)

# משתנה גלובלי למניעת התנגשויות בין חיתוכים
# אם חיתוך אחד עדיין מתבצע, הבוט לא יתחיל חיתוך חדש עד לסיום הנוכחי
is_slicing = False

def perform_slice(path):
    global is_slicing
    
# אם אין מסלול, פשוט מחזירים את המשתנה למצב לא חיתוך ומפסיקים את הפונקציה
    if not path: 
        is_slicing = False
        return
    
    # טיפול במקרה של פרי בודד: יצירת חיתוך אלכסוני אוטומטי סביב הנקודה
    if len(path) == 1:
        is_slicing = True
        x, y = path[0]
        path = [[x - 150, y + 100], [x + 150, y - 100]]
    try:
        # המרת קואורדינטות של הפריים לקואורדינטות של מסך מלא
        start_x = int(path[0][0]) + GAME_LEFT
        start_y = int(path[0][1]) + GAME_TOP

        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        # time.sleep(0.005)  # אפשר להוסיף השהייה קטנה אם צריך, אבל  נראה שהבוט עובד טוב גם בלי
        
        
        # מעבר על נקודות (בצעדים של 20) כדי להגביר את מהירות התנועה
        for i in range(1, len(path),20):
            target_x = int(path[i][0]) + GAME_LEFT
            target_y = int(path[i][1]) + GAME_TOP 

           # duration נמוך מאוד הופך את התנועה לכמעט מיידית
            pyautogui.dragTo(target_x, target_y, mouseDownUp=False, _pause=False, duration=0.1001)
            
    finally:
        # שחרור העכבר ועדכון הסטטוס גם אם קרתה שגיאה
        pyautogui.mouseUp()
        is_slicing = False

def trigger_slice(path):
    global is_slicing
    
    if not is_slicing:
        is_slicing = True
        # מריצים את perform_slice ברקע כדי לא לתקוע את מצלמת המסך
        threading.Thread(target=perform_slice, args=(path,), daemon=True).start()

def run_bot(model):
    # יצירת אובייקט מצלמה פעם אחת לשיפור ביצועים
    camera = bettercam.create(output_color="BGR")
    
    os.system('cls' if os.name == 'nt' else 'clear') # ניקוי הטרמינל לפני ההדפסה של ההוראות
    print("="*60)
    print("🚀 NINJA BOT ACTIVATED")
    print("-"*60)
    print("INSTRUCTIONS:")
    print("To STOP: Press 'ESC'")
    print("="*60)
    
    # המתנה קצרה כדי לאפשר למשתמש לעבור לחלון המשחק
    time.sleep(2)

    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("\n Stopping the bot...")
                break

            start_time = time.time()
            # לכידת הפריים הנוכחי מאזור המשחק בלבד
            frame = camera.grab(region=REGION)
            
            # אם המצלמה לא הצליחה ללכוד תמונה, נדלג לתחילת הלולאה כדי למנוע קריסה
            if frame is None:
                continue

            # עיבוד הפריים: זיהוי אובייקטים וחישוב נתיב אופטימלי
            processed_frame, full_path = process_ninja_frame(frame, model)

            # --- בדיקת תקינות המסלול לפני הביצוע ---
            # 1. full_path: מוודא שהאלגוריתם בכלל מצא נתיב ולא החזיר רשימה ריקה שמחזירה FALSE
            # 2. len > 1: מוודא שיש לפחות נקודת התחלה וסיום.

            if full_path and len(full_path) > 1:
                trigger_slice(full_path)

            # 4. חישוב והצגת מהירות הבוט בזמן אמת
            total_cycle_time = time.time() - start_time
            if total_cycle_time > 0:
                fps = 1 / total_cycle_time
                print(f"⏱️ FPS: {fps:.1f}", end='\r')

            # הצגת נקודת המבט של הבוט
            cv2.imshow('Ninja Bot Vision', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("\n Shutting down Ninja Bot...")
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_bot(model)