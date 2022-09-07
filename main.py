import cv2
import math
import random
import pickle
import time
from cvzone.HandTrackingModule import HandDetector

# Properties
width = 1280
height = 720
target_radius = 40  # pixels
hand_radius = 40  # pixels
border_size = 15  # pixels
score_text_pos = (width - 150, border_size + 30)
time_text_pos = (border_size + 15, border_size + 30)
timer_title_pos = (int(width / 2) - 150 + border_size, int(height / 2) - 20 + border_size)
object_title_pos = (int(width / 2) - 400 + border_size, int(height / 2) - 60 + border_size)

play_for_time = True
play_for_targets = not play_for_time

max_targets = 15
max_time = 20


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)  # set width of window
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  # set height of window
detector = HandDetector(detectionCon=0.8, maxHands=2)


def load_highscore(is_time):
    try:
        if is_time:
            with open('high_score_time.dat', 'rb') as file:
                score = pickle.load(file)
        else:
            with open('high_score_targets.dat', 'rb') as file:
                score = pickle.load(file)
    except:
        score = 0
    return score


def save_highscore(score, is_time):
    if is_time:
        with open('high_score_time.dat', 'wb') as file:
            pickle.dump(score, file)
    else:
        with open('high_score_targets.dat', 'wb') as file:
            pickle.dump(score, file)


class Circle:

    def __init__(self, coordinates, radius, color, thickness):
        self.coordinates = coordinates
        self.radius = radius
        self.color = color
        self.thickness = thickness

    def draw(self, _frame):
        cv2.circle(_frame, self.coordinates, self.radius, self.color, self.thickness)

    def check_intersection(self, other_coordinates, other_radius):
        distance = math.sqrt(math.pow(other_coordinates[0] - self.coordinates[0], 2) + math.pow(
            other_coordinates[1] - self.coordinates[1], 2))

        if distance <= self.radius + other_radius:
            return True
        else:
            return False


def create_random_target(current_target_pos=[]):
    if current_target_pos:
        possible_x = []

        x_limit = [target_radius + border_size + 15, width - target_radius - border_size - 15]
        y_limit = [target_radius + border_size + 15, height - target_radius - border_size - 15]

        for i in range(x_limit[0], x_limit[1]):
            if i + 100 < current_target_pos[0] or i - 100 > current_target_pos[0]:
                possible_x.append(i)

        possible_y = []
        for i in range(y_limit[0], y_limit[1]):
            if i + 100 < current_target_pos[1] or i - 100 > current_target_pos[1]:
                possible_y.append(i)

        if not possible_x:
            possible_x = range(x_limit[0], x_limit[1])

        if not possible_y:
            possible_y = range(y_limit[0], y_limit[1])

    else:
        possible_x = range(target_radius + border_size, width - target_radius - border_size)
        possible_y = range(target_radius + border_size, height - target_radius - border_size)

    random_x = random.choice(possible_x)
    random_y = random.choice(possible_y)
    random_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 256)]
    _target = Circle([random_x, random_y], target_radius, random_color, -1)

    return _target


highscore_time = load_highscore(True)
highscore_targets = load_highscore(False)


target = create_random_target()
target_count = 0
t_start = time.time()
can_reset = True
is_playing = False
timer = 5
is_reseting = False
has_reset = True

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = cv2.copyMakeBorder(frame, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT,
                               value=[0, 0, 0])

    if can_reset and not is_playing and not is_reseting and has_reset:
        t_start = time.time()
        is_reseting = True
        has_reset = False
        can_reset = False

    if is_reseting:
        elapsed_time = time.time() - t_start
        time_left = timer - elapsed_time
        if play_for_targets:
            title = "Hit as many targets as you can in " + str(max_time) + " seconds"
        else:
            title = "Hit " + str(max_targets) + " targets as fast as you can"

        frame = cv2.putText(frame, title, object_title_pos, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        frame = cv2.putText(frame, "Starting in: " + str(int(time_left)), timer_title_pos, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        if time_left <= 0:
            t_start = time.time()
            is_reseting = False
            can_reset = False
            is_playing = True
            target_count = 0

    if is_playing:
        hit_target = False
        elapsed_time = time.time() - t_start
        hands = detector.findHands(frame, flipType=False, draw=False)
        # cv2.circle(frame, target.coordinates, target.radius, target.color, target.thickness)
        target.draw(frame)

        if hands:
            for i in range(len(hands)):
                hand_position = hands[i]["center"]
                hand_circle = Circle(hand_position, hand_radius, (0, 0, 255), 1)

                if target.check_intersection(hand_circle.coordinates, hand_circle.radius):
                    # cleared
                    hand_circle.color = (0,255,0)
                    #hit_target = True
                    #break
                else:
                    hand_circle.color = (0,0,255)
                hand_circle.draw(frame)
        '''
        frame = cv2.rectangle(frame, score_text_pos, (score_text_pos[0] + 150, score_text_pos[1] - 30), (0, 0, 0), -1)
        frame = cv2.putText(frame, "Total: " + str(target_count), score_text_pos,
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

        frame = cv2.rectangle(frame, time_text_pos, (time_text_pos[0] + 200, time_text_pos[1] - 30), (0, 0, 0), -1)
        frame = cv2.putText(frame, "Time: " + "{:.2f}".format(elapsed_time), time_text_pos,
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        if hit_target:
            target_count += 1
            target = create_random_target(target.coordinates)
            if play_for_time and target_count == max_targets:
                # save highscore and reset game
                can_reset = True
                is_playing = False
                final_message = "Congrats! You hit " + str(target_count) + " targets in " \
                                + "{:.2f}".format(elapsed_time) + " seconds"
                if elapsed_time < highscore_time or highscore_time == 0:
                    save_highscore(elapsed_time, True)
                    highscore_message = "New highscore!!"
                else:
                    highscore_message = "Best score: " + "{:.2f}".format(highscore_time)

        if play_for_targets:
            if elapsed_time >= max_time:
                can_reset = True
                is_playing = False
                final_message = "Time's up! You hit " + str(target_count) + " targets in " \
                                + str(max_time) + " seconds"
                if target_count > highscore_targets or highscore_targets == 0:
                    save_highscore(target_count, False)
                    highscore_message = "New highscore!!"
                else:
                    highscore_message = "Best score: " + str(highscore_targets)

    if can_reset:
        frame = cv2.rectangle(frame, object_title_pos, (object_title_pos[0] + 800, object_title_pos[1] - 30), (0, 0, 0), -1)
        frame = cv2.putText(frame, final_message, object_title_pos, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        frame = cv2.rectangle(frame, timer_title_pos, (timer_title_pos[0] + 300, timer_title_pos[1] - 30), (0, 0, 0), -1)
        frame = cv2.putText(frame, highscore_message, timer_title_pos, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        '''

    cv2.imshow("Reaction Game", frame)

    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break
    elif k == ord('r') and can_reset:
        has_reset = True


cap.release()
cv2.destroyAllWindows()


