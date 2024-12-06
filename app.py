import streamlit as st
import tensorflow as tf
from PIL import Image
import cv2
import numpy as np
import gdown
import os

st.set_page_config(
    page_title="Car Parts Classification",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource(show_spinner=False)
def load_model():
    try:
        model_path = 'models/best_model.keras'
        if not os.path.exists('models'):
            os.makedirs('models')
        if not os.path.exists(model_path):
            with st.spinner('Downloading model... Please wait.'):
                model_url = "https://drive.google.com/uc?id=1R-_GlagW4C7qelQWaDgh9xJ_Ym6qXr6V"
                gdown.download(model_url, output=model_path, quiet=True)
        return tf.keras.models.load_model(model_path)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

class_names = [
    'AIR COMPRESSOR', 'ALTERNATOR', 'BATTERY', 'BRAKE CALIPER', 'BRAKE PAD',
    'BRAKE ROTOR', 'CAMSHAFT', 'CARBERATOR', 'CLUTCH PLATE', 'COIL SPRING',
    'CRANKSHAFT', 'CYLINDER HEAD', 'DISTRIBUTOR', 'ENGINE BLOCK', 'ENGINE VALVE',
    'FUEL INJECTOR', 'FUSE BOX', 'GAS CAP', 'HEADLIGHTS', 'IDLER ARM',
    'IGNITION COIL', 'INSTRUMENT CLUSTER', 'LEAF SPRING', 'LOWER CONTROL ARM',
    'MUFFLER', 'OIL FILTER', 'OIL PAN', 'OIL PRESSURE SENSOR', 'OVERFLOW TANK',
    'OXYGEN SENSOR', 'PISTON', 'PRESSURE PLATE', 'RADIATOR', 'RADIATOR FAN',
    'RADIATOR HOSE', 'RADIO', 'RIM', 'SHIFT KNOB', 'SIDE MIRROR', 'SPARK PLUG',
    'SPOILER', 'STARTER', 'TAILLIGHTS', 'THERMOSTAT', 'TORQUE CONVERTER',
    'TRANSMISSION', 'VACUUM BRAKE BOOSTER', 'VALVE LIFTER', 'WATER PUMP',
    'WINDOW REGULATOR'
]

class_info = {
    'Ignition Coil': 'Description of Ignition Coil.',
    'Leaf Spring': 'Description of Leaf Spring.',
}

def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = tf.image.resize(img, [224, 224])
    img = img / 255.0
    return np.expand_dims(img, axis=0)

def predict(model, img):
    prediction = model.predict(img, verbose=0)
    predicted_class_idx = np.argmax(prediction[0])
    confidence = prediction[0][predicted_class_idx]
    return class_names[predicted_class_idx], confidence, prediction[0]

def get_webcam():
    for idx in range(4):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            return cap
    return None

def main():
    st.title("Car Parts Classification")
    st.subheader("Upload an image or use the webcam to classify car parts")

    model = load_model()
    if model is None:
        st.error("Failed to load model. Please refresh the page.")
        return

    option = st.sidebar.radio("Select Input Method:", ["Upload Image", "Webcam"])

    if option == "Upload Image":
        uploaded_file = st.file_uploader("Upload a car part image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            img_array = np.array(image)
            processed_img = preprocess_image(img_array)

            with st.spinner("Analyzing image..."):
                class_name, confidence, all_predictions = predict(model, processed_img)

            st.subheader("Prediction Results")
            st.markdown(f"**Predicted Class:** {class_name}")
            st.markdown(f"**Confidence:** {confidence:.1%}")

            st.markdown("### Class Probabilities")
            for i, name in enumerate(class_names):
                st.progress(float(all_predictions[i]))
                st.caption(f"{name}: {all_predictions[i]:.1%}")

            st.markdown("### Part Description")
            st.markdown(class_info.get(class_name, "No description available."))

    else:
        st.write("Click the button below to start the webcam.")
        if st.button("Start Webcam"):
            cap = get_webcam()
            if cap is None:
                st.error("No webcam found. Please ensure it's connected and permissions are granted.")
                return

            stframe = st.empty()
            stop_button = st.button("Stop Webcam")
            
            try:
                while not stop_button:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    processed_frame = preprocess_image(frame)
                    class_name, confidence, _ = predict(model, processed_frame)

                    cv2.putText(frame, f"{class_name} ({confidence:.1%})", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_column_width=True)

                    if stop_button:
                        break

            finally:
                cap.release()

if __name__ == "__main__":
    main()
