def Raise(num,e):
    error = "\u001b[1;31m[+]\u001b[0m"
    match(num):
        case 1:
            print(f"{error} Error: No such file or directory:{e}")
            exit(0)
        case 2:
            print(f"{error} Error -- There was a problem with the segmentation module, please check dependencies:{e}")
            exit(0)
        case 3:
            print(f"{error} Error -- API error, please revise the key variable is set correctly:{e}")
            exit(0)
        case 4:
            print(f"{error} Error -- Permission or path error:{e}")
            exit(0)
        case 5:
            print(f"{error} Error -- In analysis module, possible codex failure:{e}")
            exit(0)
        case 6:
            print(f"{error} Error -- While creating all the segmented folder:{e}")
            exit(0)
        case 7:
            print(f"{error} Error -- There was a problem with the ffmpeg module, please check dependencies and directory:{e}")
            exit(0)
        case 8:
            print(f"{error} Error -- Noise recognition module error, please revise the installation reuirements:{e}")
            exit(0)
    return