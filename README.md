# Maple_Autocuber
A simple python file for players who are too lazy to manually cube their familiars. 
Note: bot is created and tested for SWORDIEMS. However it should be able to work for all maplestory servers. Can be used to cube item potential lines with a little tweaking.

Video on how to setup in game: https://youtu.be/9U0pX_-GGMM

HOW TO RUN BOT:

1. Install required packages:
    - Python 3 (https://www.python.org/downloads/) - download and install
    - Tesseract OCR (https://linuxhint.com/install-tesseract-windows/) - required for text recognition
    
    Then install Python packages using one of these methods:
    
    **Option A (Recommended):** Install all packages at once using requirements.txt:
    ```
    pip install -r requirements.txt
    ```
    
    **Option B:** Install packages individually:
    - pip install numpy
    - pip install opencv-python
    - pip install pywin32
    - pip install keyboard
    - pip install pytesseract
    - pip install pyautogui
    - pip install Pillow

2. **Run the GUI (Recommended):**
   - Open `botUI.py` in your IDE. IMPORTANT: RUN YOUR IDE IN ADMINISTRATOR MODE!
   - Configure your desired settings in the GUI (stat thresholds, roll checks, etc.)
   - Click "Start Bot" to begin

   **OR run directly:**
   - Open file "bot_logic.py" in your IDE. IMPORTANT: RUN YOUR IDE IN ADMINISTRATOR MODE!
   - Configure settings in the code (stat thresholds, which checks to enable)
   - Run the script

3. (For direct run only) Add a function to stop the bot when you get the lines you desire. 
    Example: Stop the bot when 2 lines of boss damage is rolled
        
        def check_roll_2L_BD(self):
        
        if self.line1 in single_lines_dict["BD"] and self.line2 in single_lines_dict['BD']:
            
            self.stop_bot = True
            
            return print(self.line1,self.line2,"    PASS")
    
    See dictionary at line 7/8 of file to see your options, or add your own to the dictionary.
4. Open maplestory game and place cubing UI at the top left of your screen.
5. Note that full screen maplestory is not supported. Please change your maplestory game into windowed mode.
6. Note that 1980x1080 resolution is not supported and might cause errors. Use resolution 1366x768 to be safe.

Good luck and have fun :D
