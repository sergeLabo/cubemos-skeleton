
import cv2
import numpy as np
from time import time

def overlay(src1, alpha, src2, beta):
    """
    Python: cv2.addWeighted(src1, alpha, src2, beta, gamma[, dst[, dtype]]) → dst¶
    Python: cv.AddWeighted(src1, alpha, src2, beta, gamma, dst) → None

    Parameters:
    src1 – first input array.
    alpha – weight of the first array elements.
    src2 – second input array of the same size and channel number as src1.
    beta – weight of the second array elements.
    dst – output array that has the same size and number of channels as the
            input arrays.
    gamma – scalar added to each sum.
    dtype – optional depth of the output array; when both input arrays have
            the same depth, dtype can be set to -1, which will be equivalent
            to src1.depth().
    """

    (x, y) = (src1.shape[0], src1.shape[1])
    dst = np.zeros((x, y, 3), dtype = "uint8")
    cv2.addWeighted(src1, alpha, src2, beta, 1.0, dst)

    return dst


def viewer():
    # test est un string
    img = cv2.imread("sun_sea.png")
    cursor = cv2.imread("yellow_cursor.png")
    t0 = time()
    num = 0
    cv2.namedWindow('Image',
                    cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO+cv2.WINDOW_AUTOSIZE)
    while num < 2000:
        x = int(num/2)
        y = int(num/4)
        new_img = simple_overlay(img.copy(), cursor, x, y)
        if new_img.any():
            cv2.imshow('Image', new_img)
        else:
            break
        num += 1
        if cv2.waitKey(1) == 27:
            break
    temps = int(time() - t0)
    print("Durée du test", temps)  # 10/1000=10ms
    cv2.destroyAllWindows()


def simple_overlay(background, overlay, x, y):
    (rows, cols, channels) = overlay.shape

    overlay = cv2.addWeighted(  background[y:y+rows, x:x+cols],
                                1,
                                overlay,
                                0.5,
                                0)

    background[y:y+rows, x:x+cols ] = overlay
    return background


def video():
    cap = cv2.VideoCapture('200116_Lens effect_4k_070.mov')
    back = cv2.imread('sun_sea_hd.png')
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(frame, (1280, 720))
        back = simple_overlay(back, gray, 0, 0)
        cv2.imshow('frame', back)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # #viewer()
    video()
