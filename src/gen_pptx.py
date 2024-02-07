import collections.abc
from pptx import Presentation
from pptx.util import Inches
import re
import random
import make_prompt
import get_llm


def create_ppt_text(prompt, slides, info=""):
    final_prompt = make_prompt.make_prompt(prompt, slides, info)
    #print("Prompt for the api:\n\n" + final_prompt)
    request = {
        'prompt': final_prompt,
        'max_new_tokens': 2048,
        'do_sample': True,
        'temperature': 0.6,
        'top_p': 0.1,
        'typical_p': 1,
        'repetition_penalty': 1.18,
        'top_k': 50,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': ["USER:"]
    }

    return "Title:" + get_llm.get_llm(final_prompt)

def create_ppt(text_file, ppt_name, design_number):
    prs = Presentation(f"Designs/Design-{design_number}.pptx")
    slide_count = 0
    header = ""
    content = ""
    last_slide_layout_index = -1
    firsttime = True

    with open(text_file, 'r') as file:
        lines = file.readlines()

    with open(text_file, 'w') as file:
        for line in lines:
            # Remove 8 leading spaces
            line = line[8:] if line.startswith(' ' * 8) else line
            line = line.lstrip('\t')
            file.write(line)
    
    with open(text_file, 'r', encoding='utf-8') as f: # This is the function for generating the powerpoint. You're a real pro if you understand this lol     
        for line_num, line in enumerate(f):
            line = line[8:] if line.startswith(' ' * 8) else line
            if line.startswith('Title:'):
                header = line.replace('Title:', '').strip()
                slide = prs.slides.add_slide(prs.slide_layouts[0])
                title = slide.shapes.title
                title.text = header
                body_shape = slide.shapes.placeholders[1]
                continue
            elif line.startswith('Slide:'):
                if slide_count > 0:
                    slide = prs.slides.add_slide(prs.slide_layouts[slide_layout_index])
                    title = slide.shapes.title
                    title.text = header
                    body_shape = slide.shapes.placeholders[slide_placeholder_index]
                    tf = body_shape.text_frame
                    tf.text = content
                content = "" 
                slide_count += 1
                slide_layout_index = last_slide_layout_index
                layout_indices = [1, 7, 8]
                while slide_layout_index == last_slide_layout_index:
                    if firsttime == True:
                        slide_layout_index = 1
                        slide_placeholder_index = 1
                        firsttime = False
                        break
                    slide_layout_index = random.choice(layout_indices)
                    if slide_layout_index == 8:
                        slide_placeholder_index = 2
                    else:
                        slide_placeholder_index = 1
                last_slide_layout_index = slide_layout_index
                continue
            elif line.startswith('Header:'):
                header = line.replace('Header:', '').strip()
                continue
            elif line.startswith('Content:'):
                content = line.replace('Content:', '').strip()
                next_line = f.readline().strip()
                while next_line and not next_line.startswith('#'):
                    content += '\n' + next_line
                    next_line = f.readline().strip()
                continue
                
        if content:
            slide = prs.slides.add_slide(prs.slide_layouts[slide_layout_index])
            title = slide.shapes.title
            title.text = header
            body_shape = slide.shapes.placeholders[slide_placeholder_index]
            tf = body_shape.text_frame
            tf.text = content
            
    prs.save(f'GeneratedPresentations/{ppt_name}.pptx')
    file_path = f"GeneratedPresentations/{ppt_name}.pptx"
    return f"{file_path}"

def generate_ppt(prompt, add_info, slides, theme):
    prompt = re.sub(r'[^\w\s.\-\(\)]', '', prompt)
    
    print("Generating the powerpoint...\n")
    
    with open(f'Cache/{prompt}.txt', 'w', encoding='utf-8') as f:
        f.write(create_ppt_text(prompt, slides, add_info))

    ppt_path = create_ppt(f'Cache/{prompt}.txt', prompt, theme)
    return str(ppt_path)