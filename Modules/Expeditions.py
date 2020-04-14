import sys
from os import path

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi

try:
    from Modules.Resources.Static_Information.Constants import mission_type_ids
except ModuleNotFoundError:
    from Resources.Static_Information.Constants import mission_type_ids





if __name__ == "__main__":
    universe = sys.argv[1]
    e = Expedition(universe)
    e.start_expeditions_loop()
    print("Done...")
