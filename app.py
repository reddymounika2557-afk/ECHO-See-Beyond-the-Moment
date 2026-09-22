import streamlit as st
from PIL import Image
import ollama
import pyttsx3
import io
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ECHO — See Beyond the Moment",
    page_icon="🌌",
    layout="wide"
)


# ============================================================
# GALAXY THEME
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(124, 58, 237, 0.25),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(168, 85, 247, 0.20),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 90%,
                rgba(91, 33, 182, 0.20),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #05020d,
                #0b0618,
                #140827
            );
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f5f3ff !important;
    }

    p, label {
        color: #ddd6fe !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(192, 132, 252, 0.35);
        background: linear-gradient(
            135deg,
            #6d28d9,
            #9333ea
        );
        color: white;
        font-weight: 700;
        min-height: 45px;
        box-shadow:
            0 8px 22px rgba(109, 40, 217, 0.25);
    }

    .stButton > button:hover {
        border-color: #e9d5ff;
        box-shadow:
            0 0 25px rgba(168, 85, 247, 0.40);
    }

    [data-testid="stFileUploader"] {
        background: rgba(20, 10, 38, 0.70);
        border: 1px dashed rgba(192, 132, 252, 0.30);
        border-radius: 18px;
        padding: 10px;
    }

    .footer-text {
        text-align: center;
        color: #7c6f9b;
        padding-top: 30px;
        font-size: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "before_image" not in st.session_state:
    st.session_state.before_image = None

if "before_result" not in st.session_state:
    st.session_state.before_result = None

if "after_image" not in st.session_state:
    st.session_state.after_image = None

if "verify_result" not in st.session_state:
    st.session_state.verify_result = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def image_to_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def extract_section(text, section_name):

    pattern = (
        rf"{re.escape(section_name)}\s*:\s*"
        rf"(.*?)(?=\n[A-Z][A-Z ]+\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return "Not available."


def analyze_image(image):

    prompt = """
You are ECHO, a physical situation reasoning assistant.

Analyze ONLY what is visibly supported by the image.

Do not invent objects, danger, spills, people, damage,
or events that are not visible.

Focus on physical relationships such as:

- position
- support
- alignment
- proximity
- obstruction
- balance
- blockage
- interaction between visible objects

Return exactly this structure:

OBSERVE:
Write a short factual description of what is visible.

RELATIONSHIP:
Explain the important physical relationship between visible objects.

CONDITION:
Choose exactly one:
NORMAL
POTENTIALLY PROBLEMATIC
UNCLEAR

POSSIBLE CONSEQUENCE:
State a plausible consequence based only on the visible situation.
If there is no meaningful consequence, say:
No obvious consequence.

RECOMMENDED ACTION:
Give one simple practical action.
If no action is needed, say:
No action needed.

CONFIDENCE:
Choose exactly one:
High
Medium
Low

Do not exaggerate.
Do not assume hidden information.
Do not make professional medical, engineering,
or safety judgments.
"""

    try:

        response = ollama.chat(
            model="qwen2.5vl:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        image_to_bytes(image)
                    ]
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:

        return f"ERROR: {error}"


def verify_images(before_image, after_image):

    prompt = """
You are ECHO's verification system.

Compare the BEFORE and AFTER images.

Determine whether the visible physical situation:

IMPROVED
WORSENED
SIMILAR

Focus only on visible changes.

Return exactly:

STATUS:
Choose one:
IMPROVED
WORSENED
SIMILAR

WHAT CHANGED:
Describe the visible difference.

REASON:
Explain why the situation changed or stayed similar.

CONFIDENCE:
Choose one:
High
Medium
Low

Do not invent changes that are not visible.
"""

    try:

        response = ollama.chat(
            model="qwen2.5vl:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        image_to_bytes(before_image),
                        image_to_bytes(after_image)
                    ]
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:

        return f"ERROR: {error}"


def speak_action(text):

    action = extract_section(
        text,
        "RECOMMENDED ACTION"
    )

    if action and action != "Not available.":

        try:

            engine = pyttsx3.init()

            engine.say(action)

            engine.runAndWait()

            engine.stop()

        except Exception:

            pass


# ============================================================
# ECHO HEADER
# ============================================================

st.title("🌌 ECHO")

st.markdown(
    "### SEE BEYOND THE MOMENT"
)

st.caption(
    "● LOCAL AI  •  VISION  •  REASONING"
)


# ============================================================
# ECHO PIPELINE
# ============================================================

st.info(
    "👁 Observe  →  🧠 Understand  →  🔗 Reason  →  "
    "🔮 Predict  →  ⚡ Act  →  ✓ Verify"
)


# ============================================================
# INTRODUCTION
# ============================================================

st.subheader(
    "Your phone doesn't just see. It understands."
)

st.write(
    "ECHO observes a physical situation, understands relationships "
    "between objects, reasons about what could happen next, "
    "recommends a practical action, and verifies the result."
)


# ============================================================
# DEMO MODE
# ============================================================

st.divider()

st.subheader("🎬 ECHO Demo Mode")

st.info(
    "Prepared examples for a reliable demonstration. "
    "These results are examples and are not live AI analysis."
)


demo_scenario = st.selectbox(
    "Choose a prepared scenario",
    [
        "📦 Unstable Stack",
        "🚪 Blocked Path",
        "🧴 Object Near Edge"
    ]
)


demo_data = {

    "📦 Unstable Stack": {
        "condition": "⚠️ POTENTIALLY PROBLEMATIC",
        "observe": (
            "Three cardboard boxes are stacked, with the top "
            "box visibly tilted and extending beyond the box below it."
        ),
        "relationship": (
            "The top box is not centered over its support surface, "
            "creating a visible overhang."
        ),
        "consequence": (
            "The top box may shift or fall if the stack is disturbed."
        ),
        "action": (
            "Center the top box on the box below it."
        ),
        "confidence": "Medium"
    },

    "🚪 Blocked Path": {
        "condition": "⚠️ POTENTIALLY PROBLEMATIC",
        "observe": (
            "A bag and several objects are placed across "
            "a visible walking path."
        ),
        "relationship": (
            "The objects occupy the available passage between "
            "the surrounding surfaces."
        ),
        "consequence": (
            "A person may need to step around the objects "
            "or could trip over them."
        ),
        "action": (
            "Move the objects away from the walking path."
        ),
        "confidence": "High"
    },

    "🧴 Object Near Edge": {
        "condition": "⚠️ POTENTIALLY PROBLEMATIC",
        "observe": (
            "A bottle is positioned very close to the edge "
            "of a raised surface."
        ),
        "relationship": (
            "The bottle remains on the surface but has limited "
            "margin from the edge."
        ),
        "consequence": (
            "The bottle could fall if the surface is bumped."
        ),
        "action": (
            "Move the bottle farther away from the edge."
        ),
        "confidence": "High"
    }
}


selected_demo = demo_data[demo_scenario]


if st.button("▶ Show Demo Analysis"):

    st.subheader("🌌 Demo Analysis")

    st.success(
        f"Condition: {selected_demo['condition']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### 👁 What ECHO Sees")

        st.write(
            selected_demo["observe"]
        )

    with col2:

        st.markdown("#### 🔗 Physical Relationship")

        st.write(
            selected_demo["relationship"]
        )

    col3, col4 = st.columns(2)

    with col3:

        st.markdown("#### 🔮 Possible Consequence")

        st.warning(
            selected_demo["consequence"]
        )

    with col4:

        st.markdown("#### ⚡ Recommended Action")

        st.success(
            selected_demo["action"]
        )

    st.markdown("### 🗺 Situation Map")

    st.info(
        f"👁 Observe: {selected_demo['observe']}"
    )

    st.info(
        f"🔗 Relationship: {selected_demo['relationship']}"
    )

    st.warning(
        f"🔮 Consequence: {selected_demo['consequence']}"
    )

    st.success(
        f"⚡ Action: {selected_demo['action']}"
    )

    st.caption(
        f"🎯 Confidence: {selected_demo['confidence']}"
    )


# ============================================================
# LIVE AI
# ============================================================

st.divider()

st.subheader("📷 Live Local AI Analysis")

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### 📸 Camera")

    camera_image = st.camera_input(
        "Capture a BEFORE image"
    )

with col2:

    st.markdown("#### 🖼 Upload")

    uploaded_image = st.file_uploader(
        "Upload a BEFORE image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )


# ============================================================
# GET BEFORE IMAGE
# ============================================================

before_image = None


if camera_image is not None:

    before_image = Image.open(
        camera_image
    ).convert("RGB")


elif uploaded_image is not None:

    before_image = Image.open(
        uploaded_image
    ).convert("RGB")


# ============================================================
# ANALYZE
# ============================================================

if before_image is not None:

    st.image(
        before_image,
        caption="BEFORE — Situation captured",
        use_container_width=True
    )

    if st.button("🧠 Analyze Situation"):

        with st.spinner(
            "ECHO is observing and reasoning..."
        ):

            result = analyze_image(
                before_image
            )

        st.session_state.before_image = before_image

        st.session_state.before_result = result

        st.session_state.after_image = None

        st.session_state.verify_result = None


# ============================================================
# DISPLAY AI RESULT
# ============================================================

if st.session_state.before_result is not None:

    result = st.session_state.before_result

    condition = extract_section(
        result,
        "CONDITION"
    )

    observe = extract_section(
        result,
        "OBSERVE"
    )

    relationship = extract_section(
        result,
        "RELATIONSHIP"
    )

    consequence = extract_section(
        result,
        "POSSIBLE CONSEQUENCE"
    )

    action = extract_section(
        result,
        "RECOMMENDED ACTION"
    )

    confidence = extract_section(
        result,
        "CONFIDENCE"
    )


    if "POTENTIALLY PROBLEMATIC" in condition.upper():

        condition_display = (
            "⚠️ POTENTIALLY PROBLEMATIC"
        )

    elif "NORMAL" in condition.upper():

        condition_display = "🟢 NORMAL"

    else:

        condition_display = "❓ UNCLEAR"


    st.divider()

    st.subheader(
        "🧠 Situation Understanding"
    )

    st.success(
        f"Current Condition: {condition_display}"
    )


    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "#### 👁 What ECHO Sees"
        )

        st.write(
            observe
        )

    with col2:

        st.markdown(
            "#### 🔗 Physical Relationship"
        )

        st.write(
            relationship
        )


    col3, col4 = st.columns(2)

    with col3:

        st.markdown(
            "#### 🔮 Possible Consequence"
        )

        st.warning(
            consequence
        )

    with col4:

        st.markdown(
            "#### ⚡ Recommended Action"
        )

        st.success(
            action
        )


    # ========================================================
    # SITUATION MAP
    # ========================================================

    st.markdown("### 🗺 Situation Map")

    st.info(
        f"👁 Observe → {observe}"
    )

    st.info(
        f"🔗 Relationship → {relationship}"
    )

    st.warning(
        f"🔮 Consequence → {consequence}"
    )

    st.success(
        f"⚡ Action → {action}"
    )

    st.caption(
        f"🎯 Confidence: {confidence}"
    )


    # ========================================================
    # VOICE
    # ========================================================

    if st.button(
        "🔊 Speak Recommended Action"
    ):

        speak_action(
            result
        )


# ============================================================
# BEFORE / AFTER VERIFICATION
# ============================================================

if st.session_state.before_image is not None:

    st.divider()

    st.subheader(
        "🔄 Verify the Situation"
    )

    st.write(
        "Take another image after making the recommended "
        "change. ECHO will compare the BEFORE and AFTER states."
    )


    after_camera = st.camera_input(
        "Capture an AFTER image"
    )


    if after_camera is not None:

        after_image = Image.open(
            after_camera
        ).convert("RGB")

        st.session_state.after_image = after_image


        st.image(
            after_image,
            caption="AFTER — Situation captured",
            use_container_width=True
        )


        if st.button(
            "🔍 Verify Change"
        ):

            with st.spinner(
                "ECHO is comparing both situations..."
            ):

                verification = verify_images(
                    st.session_state.before_image,
                    after_image
                )

            st.session_state.verify_result = verification


# ============================================================
# VERIFICATION RESULT
# ============================================================

if st.session_state.verify_result is not None:

    verification = st.session_state.verify_result

    status = extract_section(
        verification,
        "STATUS"
    )

    what_changed = extract_section(
        verification,
        "WHAT CHANGED"
    )

    reason = extract_section(
        verification,
        "REASON"
    )

    confidence = extract_section(
        verification,
        "CONFIDENCE"
    )


    if "IMPROVED" in status.upper():

        status_display = "🟢 IMPROVED"

    elif "WORSENED" in status.upper():

        status_display = "⚠️ WORSENED"

    else:

        status_display = "🟣 SIMILAR"


    st.divider()

    st.subheader(
        "🔍 Verification Result"
    )

    st.success(
        f"BEFORE → AFTER: {status_display}"
    )


    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "#### 🔄 What Changed"
        )

        st.write(
            what_changed
        )

    with col2:

        st.markdown(
            "#### 💡 Reason"
        )

        st.write(
            reason
        )


    st.caption(
        f"🎯 Verification Confidence: {confidence}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌌 ECHO — See Beyond the Moment"
)

st.caption(
    "Observe • Understand • Reason • Predict • Act • Verify"
)