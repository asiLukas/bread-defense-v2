# 🍞 Bread Defense V2 – MVP

This project is a MVP for the continuation of my original game, [Bread Defense](https://asi-lukas.itch.io/bread-defense), which I created when I was 15 and just starting out with programming
- you can find all the MVP "decisions" with prefix `MVP NOTE [index]`


## ✨ About the Project
- 📚 Developed for the **BI-PYT course** I've enrolled in the 25/26 winter semester


## 🎯 Goals
- _nice_ live underground world with day/night cycles
- 6 enemy types (MVP NOTE 1: these are unfortunately not animated due to time contrains😔 )
- 2 non-interactice NPCs with some secrets/ways to unlock special collectibles (MVP NOTE 2: again, no animation, super simple interaction kept 2 minimum...)
- 4 defense types, that the player can buy based on their collectibles/cash
- player gun, which can be upgradeable
- an inventory to hold cash and collectibles, some enemy types will be able to steal cash upon hitting (MVP NOTE 3: again, super simple inventory with a fixed amount of possible items to collect)
- simple settings menu

## 🎮 How to run this
- this isn't live on itch.io yet -> haven't made any executable, since I'm not happy with this enough to release it
```
virtualenv -p [path to your python 3.11 exec] [venv name]
pip install -r requirements.txt
python main.py
```
- NOTE: anything over python 3.8 will probably work fine
