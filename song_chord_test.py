import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="Chords & Lyrics Transposer",
    page_icon="🎵",
    layout="centered"
)

# Custom CSS for Dark Theme & Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #101010;
        color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF;
        font-weight: bold;
    }
    .song-card {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    pre {
        background-color: #1A1A1A !important;
        border: 1px solid #2A2A2A;
        padding: 15px;
        border-radius: 8px;
        color: #FFFFFF !important;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'all_songs' not in st.session_state:
    st.session_state['all_songs'] = [
        {
            "title": "Sample Song",
            "artist": "Sample Artist",
            "lyrics": "Verse 1\n<C>This is a <F>sample line with chords."
        }
    ]
if 'active_song_idx' not in st.session_state:
    st.session_state['active_song_idx'] = None
if 'transpose_level' not in st.session_state:
    st.session_state['transpose_level'] = 0

def transpose_chord(chord_str, semitones):
    scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Extract root note and remainder (e.g. C#m7 -> root: C#, remainder: m7)
    if len(chord_str) > 1 and chord_str[1] in ["#", "b"]:
        root = chord_str[:2]
        remainder = chord_str[2:]
    else:
        root = chord_str[0]
        remainder = chord_str[1:]

    # Normalize flats
    flat_to_sharp = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    if root in flat_to_sharp:
        root = flat_to_sharp[root]

    if root in scale:
        idx = scale.index(root)
        new_idx = (idx + semitones) % 12
        return scale[new_idx] + remainder
    return chord_str

def render_song_view():
    song = st.session_state['all_songs'][st.session_state['active_song_idx']]
    
    st.subheader(f"{song['title']} 🎵")
    st.caption(f"by {song['artist']}")
    
    st.write("---")
    
    # Transpose Controls
    cols = st.columns([1, 1, 1, 3])
    with cols[0]:
        if st.button("➖", key="trans_down"):
            st.session_state['transpose_level'] -= 1
    with cols[1]:
        if st.button("➕", key="trans_up"):
            st.session_state['transpose_level'] += 1
    with cols[2]:
        if st.button("Reset", key="trans_reset"):
            st.session_state['transpose_level'] = 0
            
    st.write(f"**Transpose Level:** {st.session_state['transpose_level']:+d}")
    
    # Process Lyrics/Chords
    lyrics = song['lyrics']
    buffer = ""
    html_output = "<pre style='color:#FFFFFF;'>"
    
    for char in lyrics:
        if char == "<":
            if buffer:
                html_output += buffer
                buffer = ""
            continue
        elif char == ">":
            if buffer:
                # Transpose the chord
                chords = buffer.strip().split()
                for c in chords:
                    transposed = transpose_chord(c, st.session_state['transpose_level'])
                    html_output += f"<span style='color:#3B8ED0; font-weight:bold;'>{transposed}</span> "
                buffer = ""
            continue
        buffer += char
        
    if buffer:
        html_output += buffer
        
    html_output += "</pre>"
    st.markdown(html_output, unsafe_allow_html=True)
    
    if st.button("⬅️ Back to List"):
        st.session_state['active_song_idx'] = None
        st.session_state['transpose_level'] = 0
        st.rerun()

def render_main_app():
    # If a song is actively being viewed
    if st.session_state['active_song_idx'] is not None:
        render_song_view()
    else:
        tab_list, tab_add = st.tabs(["🎵 Song List", "➕ Add a Song"])
        
        with tab_list:
            st.header("Search Songs")
            search_term = st.text_input("Search by Title or Artist", placeholder="Type to search...", label_visibility="collapsed")
            
            songs = st.session_state['all_songs']
            
            # Filter
            if search_term:
                filtered = [s for s in songs if search_term.lower() in s['title'].lower() or search_term.lower() in s['artist'].lower()]
            else:
                filtered = songs
                
            if not filtered:
                st.info("No songs added yet.")
            else:
                for idx, song in enumerate(filtered):
                    with st.container():
                        st.markdown("<div class='song-card'>", unsafe_allow_html=True)
                        st.markdown(f"**{song['title']}** • *by {song['artist']}*")
                        
                        if st.button("View Chords", key=f"view_{idx}"):
                            actual_idx = st.session_state['all_songs'].index(song)
                            st.session_state['active_song_idx'] = actual_idx
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                        
        with tab_add:
            st.header("Add New Song")
            title = st.text_input("Song Title")
            artist = st.text_input("Artist")
            lyrics = st.text_area("Lyrics & Chords (use <chord> e.g. <C>)", height=250)
            
            if st.button("Save Song"):
                if title and artist and lyrics:
                    st.session_state['all_songs'].append({
                        "title": title.strip(),
                        "artist": artist.strip(),
                        "lyrics": lyrics.strip()
                    })
                    st.success("Song saved successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all the fields.")

if __name__ == "__main__":
    render_main_app()
