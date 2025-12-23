# 🍞 Bread Defense V2 – MVP

This project is a MVP for the continuation of my original game, [Bread Defense](https://asi-lukas.itch.io/bread-defense), which I created when I was 15 and just starting out with programming


## ✨ About the Project
- 📚 Developed for the **BI-PYT course** I've enrolled in the 25/26 winter semester

## 🎯 Goals
- _nice_ live underground world with day/night cycles
- 6 enemy types
- 3 defense types, that the player can buy based on their collectibles/cash
- player gun, which can be upgradeable
- upgradeable health regeneration & other stats
- an inventory to hold cash
- simple menu
- infinite game logic with best score for MVP purposes
- things outside MVP -> proper inventory, npcs other than archers, story, better animations...

## 🎮 How to run this
- this isn't live on itch.io yet -> haven't made any executable, since I'm not happy with this enough to release it
```
git clone ...
virtualenv -p [path to your python 3.11 exec] [venv name]
activate the env based on your OS
pip install -r requirements.txt
cd src/
python main.py
```
- NOTE: anything over python 3.8 will probably work fine

## Other Notes
- I'm aware of the performance bottlenecks like the backgrounds, enemy rendering, ui rendering etc... still, this is outside of scope of this MVP
