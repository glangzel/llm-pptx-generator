import gen_pptx as gp
import time

# These are all available designs:
#Design 1 = Envelope, beige
#Design 2 = Blue Bubble
#Design 3 = Light Blue Black
#Design 4 = Black, dark
#Design 5 = wood
#Design 6 = Multicolored, Simple
#Design 7 = Black, white

# The main function
def main():
    print("Welcome to the powerpoint generator!")
    topic = input("Topic for the powerpoint: ")
    add_info = input("Consider this in the powerpoint (enter if none): ")
    if not add_info:
        add_info = ""
    slides = input("Number of slides: ")
    theme = int(input("Select theme of the powerpoint (1-7): "))
    print ("Done!\n Generated and saved under:", gp.generate_ppt(topic, add_info, slides, theme))
    
main()
