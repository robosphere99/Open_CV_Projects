import cv2
import mediapipe as mp
import pygame
import random

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set clock
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Balloon settings
balloon_radius = 30
balloon_speed = 2
balloon_list = []
pop_radius = 35

# Score
score = 0
font = pygame.font.SysFont("Arial", 30)

# Create a function to generate a new balloon at a random position
def create_balloon():
    x = random.randint(balloon_radius, screen_width - balloon_radius)
    y = screen_height + balloon_radius
    return [x, y]

# Create multiple balloons
for _ in range(5):
    balloon_list.append(create_balloon())

# Initialize MediaPipe Hand Detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# OpenCV video capture
# cap = cv2.VideoCapture("http://192.168.29.69:4747/video?640x480")
cap = cv2.VideoCapture(3)

# Game loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # OpenCV frame capture
    ret, frame = cap.read()
    if not ret:
        continue

    # Flip the frame horizontally for a mirror-like effect
    frame = cv2.flip(frame, 1)

    # Resize the frame to fit the Pygame window
    frame = cv2.resize(frame, (screen_width, screen_height))

    # Convert the frame to RGB as Mediapipe expects RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame using Mediapipe
    result = hands.process(rgb_frame)

    # Get finger tip position
    finger_x, finger_y = None, None
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get the tip of the index finger (landmark 8)
            finger_x = int(hand_landmarks.landmark[8].x * screen_width)
            finger_y = int(hand_landmarks.landmark[8].y * screen_height)

            # Draw the hand landmarks on the OpenCV frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Convert the OpenCV frame to a Pygame surface and display it as the background
    frame_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    # Update balloon positions and draw them
    for balloon in balloon_list:
        balloon[1] -= balloon_speed  # Move the balloon upwards
        if balloon[1] < -balloon_radius:
            balloon[1] = screen_height + balloon_radius  # Reset balloon position

        # Draw balloons
        pygame.draw.circle(screen, (255, 0, 0), (balloon[0], balloon[1]), balloon_radius)

        # Check if the finger is close to any balloon (pop detection)
        if finger_x is not None and finger_y is not None:
            distance = ((balloon[0] - finger_x) ** 2 + (balloon[1] - finger_y) ** 2) ** 0.5
            if distance < pop_radius:
                balloon_list.remove(balloon)
                balloon_list.append(create_balloon())  # Replace the popped balloon
                score += 1

    # Draw the finger pointer (circle) if detected
    if finger_x is not None and finger_y is not None:
        pygame.draw.circle(screen, (0, 255, 0), (finger_x, finger_y), 10)

    # Draw score
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Set FPS
    clock.tick(FPS)

    # Break the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release OpenCV resources and quit Pygame
cap.release()
cv2.destroyAllWindows()
pygame.quit()
