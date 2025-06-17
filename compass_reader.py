import pyttsx3

# Text summary — you can replace this with the full version if desired
text = """
Compass Mental Wellness Services, LLC in Seaford, Delaware combines traditional counseling with neuroscience-based treatments.
They focus on healing through compassion, innovation, and neuroplasticity—the brain's natural ability to adapt and change.
Services include psychotherapy, psychiatry, neurofeedback, biofeedback, cranial electrostimulation, virtual reality therapy, and more.

These techniques are used to address ADHD, anxiety, PTSD, depression, trauma, and developmental challenges.
Compass's team includes licensed psychologists, counselors, and a board-certified psychiatrist, with strong academic and clinical backgrounds.
They integrate talk therapy with cutting-edge tools to improve brain function and emotional regulation.

Located at 413 High Street, Seaford, DE, they offer both in-person and telehealth services.
Contact: (302) 394-6051 or visit www.cmwsllc.com to learn more.
"""

# Initialize the TTS engine
engine = pyttsx3.init()

# Optional voice settings
engine.setProperty('rate', 175)  # Speaking rate
engine.setProperty('volume', 1.0)  # Volume 0.0 to 1.0

# Save to file
engine.save_to_file(text, 'Compass_Mental_Wellness_Overview.mp3')
engine.runAndWait()

print("Audio file generated: Compass_Mental_Wellness_Overview.mp3")

