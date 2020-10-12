import numpy as np
import streamlit as st
import os.path
import logging
import typer
from typing import Tuple
from config import Config, ArtifactLocation
import traceback
import sys
from utils import load_artifacts

logging.basicConfig(level=Config.LOGGING)


def app(artifact_location: str) -> None:
    @st.cache(allow_output_mutation=True)
    def from_artifacts(artifact_location: str) -> Tuple:
        art_loc = ArtifactLocation(artifact_location)
        return load_artifacts(art_loc)

    # Here is the "frontend" code

    st.title("Predicting movie review sentiment")
    st.info(
        "Based on an example in [awesome-streamlit](https://github.com/MarcSkovMadsen/awesome-streamlit) "
        "by [Marc Skov Madsen](https://github.com/MarcSkovMadsen), "
        "who took it from [Paras Patidar](https://github.com/patidarparas13/Sentiment-Analyzer-Tool). \n\n"
        "Cheers both!\n\n"
    )
    st.write(
        "The algorithm is trained on a collection of movie reviews and you can test it below."
    )

    st.subheader("Load model artifacts")
    art_loc = ArtifactLocation(artifact_location)

    if art_loc == ArtifactLocation.LOCAL:
        text_to_print = "**0Ops**: Using local artifacts."
    elif art_loc == ArtifactLocation.S3:
        text_to_print = (
            "**AlmostOps**: Using artifacts downloaded from hardcoded S3 location."
        )
    elif art_loc == ArtifactLocation.S3_MLFLOW:
        text_to_print = "**MLOps**: Using artifacts downloaded from S3 with MLflow Tracking. Fancy stuff!"

    st.markdown(text_to_print)

    with st.spinner("Loading.."):
        feature_engineering, classifier = from_artifacts(artifact_location)
        st.info("Artifacts loaded successfully!")

    st.title("Feed the hungry model with your review!")
    write_here = "Write Here..."
    review = st.text_input(
        "Enter a review for classification by the algorithm", write_here
    )
    if st.button("Predict Sentiment"):
        y = feature_engineering.transform([review])
        prediction = classifier.predict(y)
        probability = np.round(np.amax(classifier.predict_proba(y)), 2)

        def convert(prediction: int) -> str:
            return "Positive" if prediction == 1 else "Negative"

        if review != write_here:
            st.success(
                f"*Sentiment prediction*: **{convert(prediction).upper()}** with probability {100 * probability}%"
            )
            st.balloons()
        else:
            st.error("You need to input a review for classification!")
    else:
        st.info(
            "**Enter a review** above and **press the button** to predict the sentiment."
        )


if __name__ == "__main__":
    # Need to do this try/except due to Streamlit weirdness
    # See https://github.com/streamlit/streamlit/issues/468
    try:
        typer.run(app)
    except SystemExit as e:
        if e.code != 0:
            raise
