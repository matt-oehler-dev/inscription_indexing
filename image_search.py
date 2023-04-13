import streamlit as st
import os
from PIL import Image
from typing import List
import json
import base64
from io import BytesIO


USE_SAMPLED_SET_OF_IMAGES = True

if USE_SAMPLED_SET_OF_IMAGES:
    TAG_DIR: str = "tag_files_500"
else:
    TAG_DIR: str = "tag_files"


@st.cache_data
def get_image_tags(image_filename: str, tags_file_name: str) -> List[str]:
    with open(os.path.join(TAG_DIR, tags_file_name)) as f:
        tags_dict = json.load(f)

        return tags_dict[image_filename].get("tags", [])


@st.cache_data
def get_image_captions(image_filename: str, tags_file_name: str) -> List[str]:
    with open(os.path.join(TAG_DIR, tags_file_name)) as f:
        tags_dict = json.load(f)

        return tags_dict[image_filename].get("raw", "")


@st.cache_data
def load_tags_json(tags_file_name: str):
    with open(os.path.join(TAG_DIR, tags_file_name)) as f:
        json_file = json.load(f)
    return json_file


# Define the layout of the app
def app():
    st.title("Inscription Indexing")
    st.sidebar.title("Search")

    tag_files = [x[:-5] for x in sorted(os.listdir(TAG_DIR))]
    tags_file_name: str = (
        st.sidebar.selectbox("Select Caption Source", tag_files, index=5) + ".json"
    )

    # get tags and image files
    tags_dict = load_tags_json(tags_file_name=tags_file_name)
    nested_list = [tags["tags"] for tags in tags_dict.values()]
    all_tags = list(set(sum(nested_list, [])))
    image_filenames = [k for k in tags_dict.keys()]

    # sidebar options
    selected_tags: List[str] = st.sidebar.multiselect("Select Tags", sorted(all_tags))
    caption_option: str = st.sidebar.selectbox(
        label="Caption Options",
        options=["Tags", "Captions", "InscriptionId", None],
        index=0,
    )

    images_to_show = []
    if selected_tags:
        one_hundredth = (len(tags_dict) // 100) + 1
        percent_searched = 0
        bar = st.progress(percent_searched)
        for i, inscription_id in enumerate(image_filenames):
            if i % one_hundredth == 0:
                percent_searched += 1
                # print(i, percent_searched, i % percent_searched)
                bar.progress(percent_searched)
            image_tags = get_image_tags(inscription_id, tags_file_name=tags_file_name)
            if set(selected_tags).issubset(set(image_tags)):
                images_to_show.append(inscription_id)
        bar.progress(100)
        bar.empty()

    if not selected_tags:
        st.write("Please select one or more tags to display images.")
    elif not images_to_show:
        st.write("No images found with the selected tags.")
    else:
        st.write(
            f"There are: {len(images_to_show)} images out of {len(tags_dict)} with the selected tag(s)"
        )
        page_number = st.sidebar.number_input(
            "Page number", min_value=1, max_value=len(images_to_show) // 16 + 1, value=1
        )
        start_index = (page_number - 1) * 16
        end_index = start_index + 16

        cols = st.columns(4)
        for i, inscription_id in enumerate(images_to_show[start_index:end_index]):
            if i % 4 == 0:
                cols = st.columns(4, gap="large")

            if caption_option == "Tags":
                caption = " ".join(
                    get_image_tags(
                        image_filename=inscription_id,
                        tags_file_name=tags_file_name,
                    )
                )
            elif caption_option == "Captions":
                caption = get_image_captions(
                    image_filename=inscription_id,
                    tags_file_name=tags_file_name,
                )
            elif caption_option == "InscriptionId":
                caption = inscription_id
            else:
                caption = None

            # get image
            encoded_image_data = tags_dict[inscription_id]["encoded_bytes"]
            decoded_image_data = base64.b64decode(encoded_image_data)
            image = Image.open(BytesIO(decoded_image_data))
            cols[i % 4].image(
                image,
                caption=caption,
                width=190,
            )


# Run the app
if __name__ == "__main__":
    app()
