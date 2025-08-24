###############
# CLIP FILTER #
###############
# Lets finish by modifying our rambo clip to make it sepia
import numpy as np


# We will start by defining a function that turn a numpy image into sepia
# It takes the image as numpy array in entry and return the modified image as output
def sepia_filter(frame: np.ndarray):
    # Sepia filter transformation matrix
    # Sepia transform works by applying to each pixel of the image the following rules
    # res_R = (R * .393) + (G *.769) + (B * .189)
    # res_G = (R * .349) + (G *.686) + (B * .168)
    # res_B = (R * .272) + (G *.534) + (B * .131)
    #
    # With numpy we can do that very efficiently by multiplying the image matrix by a transformation matrix
    sepia_matrix = np.array(
        [[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]
    )

    # Convert the image to float32 format for matrix multiplication
    frame = frame.astype(np.float32)

    # Apply the sepia transformation
    # .T is needed because multiplying matrix of shape (n,m) * (m,k) result in a matrix of shape (n,k)
    # what we want is (n,m), so we must transpose matrix (m,k) to (k,m)
    sepia_image = np.dot(frame, sepia_matrix.T)

    # Because final result can be > 255, we limit the result to range [0, 255]
    sepia_image = np.clip(sepia_image, 0, 255)

    # Convert the image back to uint8 format, because we need integer not float
    sepia_image = sepia_image.astype(np.uint8)

    return sepia_image


# Now, we simply apply the filter to our clip by calling image_transform, which will call our filter on every frame
rambo_clip = rambo_clip.image_transform(sepia_filter)

# Let's see how our filter look
rambo_clip.preview(fps=10)