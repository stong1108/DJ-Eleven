from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2
from datetime import datetime
from pygamemusicplayer import MusicPlayer
import pygame

class DJEleven(object):
    def __init__(self):
        self.ratio_threshold = 0.25
        self.min_frames_below_threshold = 20
        self.frame_counter = 0
        self.face_detector = dlib.get_frontal_face_detector()
        self.face_predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        self.hand_detector = dlib.fhog_object_detector('models/HandDetector.svm')
        self.blink_counter = 0
        self.hand_counter = 0
        self.min_hand_frames = 5
        self.pause_flag = False
        self.mp = MusicPlayer()

    def calc_eye_ratio(self, eye):
        '''
        eye aspect ratio remains pretty constant when eye is open
        eye aspect ratio falls to zero when eye is closed

        eye locations (x,y) coords
            0: 'p1', outer corner
            1: 'p2', outer top iris
            2: 'p3', inner top iris
            3: 'p4', inner corner
            4: 'p5', inner bottom iris
            5: 'p6', outer bottom iris
        '''
    	# vertical distances
    	A = dist.euclidean(eye[1], eye[5])
    	B = dist.euclidean(eye[2], eye[4])

    	# horizontal distance
    	C = dist.euclidean(eye[0], eye[3])

    	# compute the eye aspect ratio
    	ratio = (A + B) / (2.0 * C)

        return ratio

    def do_the_thing(self):
        pygame.display.set_mode((10, 10))
        MUSIC_ENDED = pygame.USEREVENT
        self.mp.mixer.music.set_endevent(MUSIC_ENDED)
        self.mp.start_play()

        (left1, left2) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
        (right1, right2) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

        # start video
        vs = VideoStream(src=0).start()
        fileStream = False
        time.sleep(1)

        # play next song if current song has finished
        while True:
            for event in pygame.event.get():
                if event.type == MUSIC_ENDED:
                    print 'ended'
                    self.mp.idx += 1
                    if self.mp.idx == len(self.mp.song_titles):
                        self.mp.idx = 0
                        shuffle(self.mp.order)
                    self.mp.mixer.music.load(self.mp.song_paths[self.mp.order[self.mp.idx]])
                    self.mp.mixer.music.play()

            # read frame, resize, convert to grayscale
            frame = vs.read()
            frame = imutils.resize(frame, width=450)
            grayscaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces and hands
            faces = self.face_detector(grayscaled, 0)
            hands = self.hand_detector(frame)
            # print hands
            # print len(hands)
            # for i, h in enumerate(hands):
            #     print 'Detection {}: Left: {}, Right: {}, Bottom: {}'.format(i, h.left(), h.top(), h.right(), h.bottom())

            if len(hands) > 0:
                self.hand_counter += 1
                # l_hand, t_hand, r_hand, b_hand = hands[0].left(), hands[0].top(), hands[0].right(), hands[0].bottom()
                # corner1 = (l_hand, t_hand)
                # corner2 = (r_hand, b_hand)
                # rect = cv2.rectangle(frame, corner1, corner2, (0, 255, 0), 2)
                # cv2.drawContours(frame, [rect], 0, (0, 255, 0), 2)

                if self.hand_counter >= self.min_hand_frames:
                    self.hand_counter = 0
                    self.pause_flag = self.mp.fade_pause()


            elif self.pause_flag == True:
                self.mp.resume_pause()
                self.pause_flag = False
                self.hand_counter = 0

            else:
                self.mp.mixer.music.set_volume(1)
                self.hand_counter = 0


            for face in faces:
                # get array of landmark coords
                landmarks = self.face_predictor(grayscaled, face)
                landmarks = face_utils.shape_to_np(landmarks)

                # find eyes, calc ratio
                left_eye = landmarks[left1:left2]
                right_eye = landmarks[right1:right2]
                left_ratio = self.calc_eye_ratio(left_eye)
                right_ratio = self.calc_eye_ratio(right_eye)

                avg_ratio = 0.5 * (left_ratio + right_ratio)

                # visualizing
                left_eyehull = cv2.convexHull(left_eye)
                right_eyehull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_eyehull], -1, (0,255,0), 1)
                cv2.drawContours(frame, [right_eyehull], -1, (0,255,0), 1)

                if avg_ratio < self.ratio_threshold:
                    self.frame_counter += 1
                elif self.frame_counter >= self.min_frames_below_threshold:
                        print 'BLINK: SONG CHANGE AT {}'.format(datetime.now().strftime('%I:%M:%S %p'))
                        self.blink_counter += 1
                        self.frame_counter = 0
                        self.mp.next_song()

            cv2.putText(frame, "Blinks: {}".format(self.blink_counter), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,0), 2)
            cv2.putText(frame, "Eye Aspect Ratio: {:.2f}".format(avg_ratio), (250,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 2)
            cv2.putText(frame, "Hand Frame Counter: {}".format(self.hand_counter), (100,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 2)

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        vs.stop()


if __name__ == '__main__':
    dj = DJEleven()
    dj.do_the_thing()
