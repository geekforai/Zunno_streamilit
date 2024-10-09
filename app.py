import streamlit as st
from utiils import color_schemes, industries, seasons, moods
import os
from clip import ImageTextMatcher
from PIL import Image
from server_utils import (
    sam_method,
    get_text_LLM_answer,
    generate_prompt,
    image_generation,
    generate_text,
    inpaint_image,
    paste_image,
    remove_text
)
from image_utils import draw_multiline_text_in_bbox
from rembg import remove

def handle_submit(p_name, prompt, p_color, s_color, color_scheme, industry,
                  target_audience, season, mood, visual_elements, logo, product):
    global template_matcher
    template_matcher = ImageTextMatcher()
    st.session_state.p_name = p_name
    if 'isTemplatesLoaded' not in st.session_state:
        st.session_state.isTemplatesLoaded = False
    if not st.session_state.isTemplatesLoaded or template_matcher.image_embeddings is None:
        print('Creating Embeddings')
        template_matcher.load_images_and_create_embeddings('templates')
        st.session_state.isTemplatesLoaded = True

    # Fetch images based on user input
    templates = template_matcher.fetch_images_based_on_text(
        f"{p_name} {prompt} {industry} {target_audience} {season} {mood}"
    )

    # Create a dictionary of images
    st.session_state.image_dict = {
        'Image 1': os.path.join('templates', templates[0]),
        'Image 2': os.path.join('templates', templates[1]),
        'Image 3': os.path.join('templates', templates[2]),
        'Image 4': os.path.join('templates', templates[3])
    }

    # Set the default selected image to the first image
    st.session_state.selected_image_name = 'Image 1'

def update_image(selected_image_name):
    """Update the displayed image based on the selection."""
    selected_image = st.session_state.image_dict[selected_image_name]
    st.image(selected_image, caption=f"Selected: {selected_image_name}", use_column_width=True)
    Image.open(selected_image).resize((512, 512)).save(selected_image)
    selected_image_image = Image.open(selected_image)
    title_bbox, subtitle_bbox, product_bbox = sam_method(selected_image, f'title,hashtags,{st.session_state.p_name}')
    image_without_text = remove_text(selected_image)
    image_without_text.save('image_without_text.png')
    print(product_bbox)
    empty_image = inpaint_image('image_without_text.png', product_bbox)
    empty_image.save('empty_image.png')
    title, subtitle, hashtags = get_text_LLM_answer(st.session_state.promot_to_title)
    image_with_new_title = draw_multiline_text_in_bbox(empty_image, title, title_bbox)
    image_with_new_title.save('image_with_new_title.png')
    product_image = Image.open(st.session_state.product)
    product_without_bg = remove(product_image)
    product_without_bg.save('product_without_bg.png')
    image_with_product = paste_image('image_with_new_title.png', 'product_without_bg.png', product_bbox)

    image_with_product.save('intermidiate.png')
    # st.image(image_with_product)
    print(st.session_state.promot_to_title)
    output = image_generation('intermidiate.png', prompt=generate_prompt(st.session_state.promot_to_title))
    output.save('output.png')
    image_with_new_title = draw_multiline_text_in_bbox(output, title, title_bbox)
    image_with_new_title.save('image_with_new_title.png')
    output = draw_multiline_text_in_bbox(output, subtitle, subtitle_bbox)
    output.save('output.png')
    output = paste_image('output.png', 'product_without_bg.png', product_bbox)
    st.write('Output')
    st.image(output)

with st.form(key='form'):
    p_name = st.sidebar.text_input(label='Product Name')
    prompt = st.sidebar.text_area(label='Prompt')
    p_color = st.sidebar.text_input(label='Enter primary color')
    s_color = st.sidebar.text_input(label='Enter secondary color')
    color_scheme = st.sidebar.selectbox(label='Select Color scheme', options=color_schemes)
    industry = st.sidebar.selectbox(label='Select Industry', options=industries)
    target_audience = st.sidebar.text_input(label='Target Audience')
    season = st.sidebar.selectbox(label='Select Season', options=seasons)
    mood = st.sidebar.selectbox(label='Select Moods', options=moods)
    visual_elements = st.sidebar.multiselect(label='Select visual elements', options=['Icons', 'Illustrations', 'Photography'])
    logo = st.sidebar.file_uploader(label='Upload Logo', type=["png"])
    product = st.sidebar.file_uploader(label='Upload Product image', type=["png", "jpg", "jpeg"])
    submit = st.form_submit_button(label='Initialize')
    st.session_state.product = product
    st.session_state.promot_to_title = f"""
            Generate a high-quality image for {p_name} and user prompt {prompt} that embodies the '{color_scheme}' theme during the {season} season, specifically crafted for the {industry} industry. 
            audience of {target_audience}, conveying a {mood} mood. 
            Use a {color_scheme} color scheme with {p_color} as the dominant color and {s_color} and visual elements {visual_elements} as a complementary accent. and it should not be blurry 
            """
    if submit:
        

        handle_submit(p_name, prompt, p_color, s_color, color_scheme, industry, target_audience, season, mood, visual_elements, logo, product)

    
if 'image_dict' in st.session_state:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.image(st.session_state.image_dict['Image 1'], caption="Image 1", use_column_width=True)
        with col2:
            st.image(st.session_state.image_dict['Image 2'], caption="Image 2", use_column_width=True)
        with col3:
            st.image(st.session_state.image_dict['Image 3'], caption="Image 3", use_column_width=True)
        with col4:
            st.image(st.session_state.image_dict['Image 4'], caption="Image 4", use_column_width=True)

        # Select the image
        if selected_image_name := st.selectbox("Select an image", options=list(st.session_state.image_dict.keys()), index=None):
            # Update the displayed image
            update_image(selected_image_name)
