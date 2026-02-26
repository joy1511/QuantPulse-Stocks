"""
Extract weights from the local model and save as .weights.h5
This is version-independent — only numpy arrays, no architecture serialization.
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
print(f"TF: {tf.__version__}, Keras: {tf.keras.__version__}")

# Load using .h5 (works locally since we have the same Keras that created it)
print("Loading model from models/universal_lstm.h5 ...")
model = tf.keras.models.load_model("models/universal_lstm.h5", compile=False)
print(f"✅ Loaded. Input: {model.input_shape}, Output: {model.output_shape}")
model.summary()

# Save ONLY the weights (no architecture, no serialization issues)
weights_path = "models/universal_lstm.weights.h5"
model.save_weights(weights_path)
print(f"\n✅ Weights saved to: {weights_path}")
print(f"   File size: {os.path.getsize(weights_path) / 1024:.1f} KB")
print("\nDone! Upload this with:")
print(f"  huggingface-cli upload joy1511/QuantPulse-Models {weights_path} universal_lstm.weights.h5")
