from epd_lib import EPD_4in2
from FONTS import cntr_st


def loading(epd):
    epd.image1Gray.fill(epd.white)

    epd.EPD_4IN2_V2_Init()
    cntr_st("Loading ...", 130, 3, epd, epd.width)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)


def lead_xbm_header(file_path):
    width = 0
    height = 0
    depth = 0

    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("#define"):
                key_value = line.strip().split(" ")
                if key_value[1] == "width":
                    width = int(key_value[2])
                elif key_value[1] == "height":
                    height = int(key_value[2])
                elif key_value[1] == "depth":
                    depth = int(key_value[2])
            else:
                break

    return width, height, depth


def load_image_1bit_xbm(file_path, size, position, epd):
    epd.image1Gray.fill(epd.white)

    epd.EPD_4IN2_V2_Init()
    print("Loading 1-bit image ...")

    with open(file_path, "r") as file:
        x = 0
        y = 0
        
        for line in file:
            if line.startswith("#define"):
                continue

            hex_data = line.strip().split(" ")
            for data in hex_data:
                if data.startswith("0x"):
                    data = data[2:]
                byte = int(data, 16)

                for i in range(7, -1, -1):
                    if x >= epd.width:
                        x += 1
                        continue

                    pixel_value = (byte & (1 << i)) >> i
                    if pixel_value == 0:
                        epd.image1Gray.pixel(position[0] + x, position[1] + y, epd.black)
                    else:
                        epd.image1Gray.pixel(position[0] + x, position[1] + y, epd.white)
                    x += 1

                    if x >= size[0]:
                        x = 0
                        y += 1

    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)


def load_image_2bit_xbm(file_path, size, position, epd):
    epd.image4Gray.fill(epd.white)

    epd.EPD_4IN2_V2_Init_4Gray()
    print("Loading 2-bit image ...")

    with open(file_path, "r") as file:
        x = 0
        y = 0

        for line in file:
            if line.startswith("#define"):
                continue

            hex_data = line.strip().split(" ")
            for data in hex_data:
                if data.startswith("0x"):
                    data = data[2:]
                byte = int(data, 16)

                read_mask = 0xC0 # 11000000
                for i in range(3, -1, -1):
                    if x >= epd.width:
                        x += 1
                        continue

                    pixel_value = (byte & read_mask) >> i * 2
                    if pixel_value == 0:
                        epd.image4Gray.pixel(position[0] + x, position[1] + y, epd.black)
                    elif pixel_value == 1:
                        epd.image4Gray.pixel(position[0] + x, position[1] + y, epd.darkgray)
                    elif pixel_value == 2:
                        epd.image4Gray.pixel(position[0] + x, position[1] + y, epd.grayish)
                    else:
                        epd.image4Gray.pixel(position[0] + x, position[1] + y, epd.white)
                    read_mask >>= 2
                    x += 1

                    if x >= size[0]:
                        x = 0
                        y += 1                

    epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)




if __name__=='__main__':
    epd = EPD_4in2()

    loading(epd)

    #image_path = "Badge_Image_400x300_1bit.xbm"
    image_path = "Badge_Image_400x300_2bit.xbm"
    #image_path = "img_400x267_1bit.xbm"
    #image_path = "img_400x267_2bit.xbm"
    #image_path = "dog_200x195_2bit.xbm"    
    #image_path = "chips_400x300_2bit.xbm"
    #image_path = "Muster_Badge_400x300_2bit.xbm"
    image_width = 400
    image_height = 300
    image_depth = 1 # 1-bit image
    
    position = (0, 0) # Starting position for the image
    calc_pos = True

    
    width, height, depth = lead_xbm_header(image_path)
    if width > 0:
        image_width = width
    if height > 0:
        image_height = height
    if depth > 0:
        image_depth = depth
    print(f"Image width: {image_width}, height: {image_height}, depth: {image_depth}")

    if calc_pos:
        # Calculate the position to center the image on the screen
        position = ((epd.width - image_width) // 2, (epd.height - image_height) // 2)

    if image_depth == 1:
        load_image_1bit_xbm(image_path, (image_width, image_height), position, epd)
    elif image_depth == 2:
        load_image_2bit_xbm(image_path, (image_width, image_height), position, epd)
    else:
        print("Unsupported image depth. Please use 1 or 2 bits.")

    print("Enter sleep mode")
    epd.Sleep()