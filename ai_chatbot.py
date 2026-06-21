import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import webbrowser
import random
import speech_recognition as sr
import threading
import json  # <-- Import the JSON library

# --- Database (REMOVED) ---
# The old symptom_db and disease_db are GONE.
# We will now load them from a file.

responses = {
    "hi": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm doing well, thank you!", "Great, thanks for asking!"],
    "bye": ["Goodbye!", "See you later!", "Bye! Stay healthy."],
    "help": "I can help with a few things. Try clicking one of the buttons below!",
}

class MedicalChatBot(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Medical ChatBot")
        self.geometry("450x600")
        self.configure(bg="#f0f4f7")

        self.defaultFont = tkFont.Font(family="Arial", size=10)
        self.boldFont = tkFont.Font(family="Arial", size=10, weight="bold")

        self.current_state = "NORMAL"

        # --- NEW: Load the database ---
        self.disease_db = {}
        self.symptom_to_disease_map = {}
        self.load_database("medical_data.json")
        # ------------------------------

        # --- FIX: Swapped order ---
        self.init_widgets() 
        self.init_styles()
        # --------------------------
        
        self.add_log("Bot", "Hello! I'm your medical assistant. How can I help you? Try clicking a button below.", "info")

    def load_database(self, filename):
        """Loads the medical database from a JSON file and builds the symptom map."""
        try:
            with open(filename, 'r') as f:
                self.disease_db = json.load(f)
            
            # Now, build the reverse map (symptom -> list of diseases)
            self.symptom_to_disease_map = {}
            for disease_key, data in self.disease_db.items():
                for symptom in data["symptoms"]:
                    if symptom not in self.symptom_to_disease_map:
                        self.symptom_to_disease_map[symptom] = []
                    self.symptom_to_disease_map[symptom].append(disease_key)
            
            print("Database loaded successfully.")
            print(f"Loaded {len(self.disease_db)} diseases.")
            print(f"Mapped {len(self.symptom_to_disease_map)} unique symptoms.")

        except FileNotFoundError:
            print(f"ERROR: Database file '{filename}' not found.")
            # Handle this error gracefully in a real app
            self.add_log("Bot", f"FATAL ERROR: Database file '{filename}' not found. The app cannot function.", "bot_bubble")
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode JSON from '{filename}'.")
            self.add_log("Bot", f"FATAL ERROR: Database file '{filename}' is corrupted. The app cannot function.", "bot_bubble")
        except Exception as e:
            print(f"An unexpected error occurred loading the database: {e}")

    def init_styles(self):
        """Initialize custom styles for ttk widgets."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background="#f0f4f7", font=self.defaultFont)
        
        # --- Chat Log Styles ---
        self.chat_log.tag_configure("user_bubble",
            background="#007aff",
            foreground="white",
            font=self.boldFont,
            justify="right",
            wrap="word",
            relief="raised",
            borderwidth=1,
            lmargin1=50,
            rmargin=10,
            spacing3=10
        )
        self.chat_log.tag_configure("bot_bubble",
            background="#e5e5ea",
            foreground="black",
            font=self.defaultFont,
            justify="left",
            wrap="word",
            relief="raised",
            borderwidth=1,
            lmargin1=10,
            rmargin=50,
            spacing3=10
        )
        self.chat_log.tag_configure("info_message",
            foreground="#555555",
            font=("Arial", 9, "italic"),
            justify="center",
            wrap="word",
            spacing3=10
        )

        # --- Button Styles ---
        style.configure("TButton",
            font=self.boldFont,
            background="#007aff",
            foreground="white",
            borderwidth=0,
            padding=10
        )
        style.map("TButton",
            background=[("active", "#0056b3")]
        )
        
        style.configure("Voice.TButton",
            background="#5856d6",
        )
        style.map("Voice.TButton",
            background=[("active", "#3f3d99")]
        )

        style.configure("TEntry",
            font=self.defaultFont,
            padding=10,
            borderwidth=0
        )

    def init_widgets(self):
        """Create and lay out all widgets using .grid()"""
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_log = tk.Text(chat_frame,
            bd=0,
            bg="#ffffff",
            font=self.defaultFont,
            wrap="word",
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_log.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_log["yscrollcommand"] = scrollbar.set

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ttk.Button(
            button_frame, text="Symptom Checker", command=self.set_symptom_mode
        ).grid(row=0, column=0, sticky="ew", padx=2)
        
        ttk.Button(
            button_frame, text="Disease Info", command=self.set_disease_mode
        ).grid(row=0, column=1, sticky="ew", padx=2)

        ttk.Button(
            button_frame, text="Book Appointment", command=self.open_appointment_website
        ).grid(row=0, column=2, sticky="ew", padx=2)

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky="ew")
        
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)
        input_frame.grid_columnconfigure(2, weight=0)

        self.user_input = ttk.Entry(input_frame, style="TEntry")
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message_event)

        self.voice_button = ttk.Button(
            input_frame,
            text="🎤",
            style="Voice.TButton",
            width=3,
            command=self.activate_voice_input_thread
        )
        self.voice_button.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            width=6,
            command=self.send_message_event
        )
        self.send_button.grid(row=0, column=2, sticky="ew")

    # --- UI & State Functions ---

    def add_log(self, sender, message, tag):
        """Adds a message to the chat log with the correct style."""
        self.chat_log.config(state=tk.NORMAL)
        
        if sender == "Bot":
            self.chat_log.insert(tk.END, f"Bot:\n{message}\n\n", tag)
        elif sender == "You":
            self.chat_log.insert(tk.END, f"You:\n{message}\n\n", tag)
        else:
            self.chat_log.insert(tk.END, f"{message}\n\n", tag)
            
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.yview(tk.END)

    def set_symptom_mode(self):
        self.current_state = "CHECK_SYMPTOMS"
        self.add_log("Bot", "Please enter your symptoms, separated by commas (e.g., fever, cough).", "bot_bubble")

    def set_disease_mode(self):
        self.current_state = "DISEASE_INFO"
        self.add_log("Bot", "Please enter the name of a single disease you want to know about.", "bot_bubble")

    def open_appointment_website(self):
        self.add_log("Bot", "Opening the appointment website for you...", "bot_bubble")
        booking_url = "[https://docpulse.com/products/online-doctor-appointment-app/](https://docpulse.com/products/online-doctor-appointment-app/)"
        webbrowser.open_new(booking_url)

    # --- Message Handling ---

    def send_message_event(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        self.add_log("You", user_message, "user_bubble")
        self.user_input.delete(0, tk.END)
        self.process_message(user_message)

    def process_message(self, user_message):
        """The core logic for handling user input based on state."""
        
        # Standardize the input for lookups
        processed_input = user_message.lower().strip()

        if processed_input == "exit":
            self.destroy()
            return

        if processed_input in responses:
            self.add_log("Bot", random.choice(responses[processed_input]), "bot_bubble")
            self.current_state = "NORMAL"
            return
            
        if self.current_state == "CHECK_SYMPTOMS":
            # Standardize symptom inputs
            symptom_keys = [
                s.strip().replace(" ", "_") for s in processed_input.split(",")
            ]
            response = self.check_symptoms(symptom_keys)
            self.add_log("Bot", response, "bot_bubble")
            self.add_log("Info", "I am a bot. Please consult a real doctor for a proper diagnosis.", "info_message")
            self.current_state = "NORMAL"

        elif self.current_state == "DISEASE_INFO":
            # Standardize disease name for lookup
            disease_key = processed_input.replace(" ", "_")
            response = self.get_disease_info(disease_key)
            self.add_log("Bot", response, "bot_bubble")
            self.current_state = "NORMAL"
        
        else:
            self.add_log("Bot", "I'm sorry, I didn't understand that. Please try again or use one of the buttons.", "bot_bubble")

    # --- Voice Handling (in a thread) ---

    def activate_voice_input_thread(self):
        self.voice_button.config(state=tk.DISABLED, text="...")
        threading.Thread(target=self.send_voice_message, daemon=True).start()

    def send_voice_message(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.add_log("Info", "Listening... Please speak.", "info_message")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                self.add_log("Info", "Listening timed out. Please try again.", "info_message")
                self.voice_button.config(state=tk.NORMAL, text="🎤")
                return

        try:
            user_message_voice = recognizer.recognize_google(audio)
            self.add_log("You", f"(Voice): {user_message_voice}", "user_bubble")
            self.process_message(user_message_voice)
        except sr.UnknownValueError:
            self.add_log("Bot", "Sorry, I could not understand the audio. Please try typing.", "bot_bubble")
        except sr.RequestError:
            self.add_log("Bot", "Could not request results. Check your internet connection.", "bot_bubble")
        
        self.voice_button.config(state=tk.NORMAL, text="🎤")

    # --- Core Logic Functions (UPDATED) ---

    def check_symptoms(self, symptom_keys):
        """Checks symptoms against the dynamically built symptom map."""
        if not self.symptom_to_disease_map:
            return "ERROR: The symptom database is not loaded."

        matched_diseases = []
        unknown_symptoms = []
        
        for symptom in symptom_keys:
            if symptom in self.symptom_to_disease_map:
                matched_diseases.extend(self.symptom_to_disease_map[symptom])
            else:
                unknown_symptoms.append(symptom)

        if not matched_diseases:
            return "Your symptoms do not match any specific condition in my database. Please consult a healthcare professional."

        disease_counts = {}
        for d in matched_diseases:
            disease_counts[d] = disease_counts.get(d, 0) + 1
        
        sorted_diseases = sorted(disease_counts.items(), key=lambda item: item[1], reverse=True)

        response = "Based on your symptoms, here are some possibilities:\n\n"
        
        for disease_key, count in sorted_diseases[:3]:
            if disease_key in self.disease_db:
                disease = self.disease_db[disease_key]
                response += f"**{disease['display_name']}** (Matched {count} symptoms)\n"
                response += f"Description: {disease['description']}\n"
                response += f"Suggested Care: {disease['care']}\n\n"
        
        if unknown_symptoms:
            response += f"Note: I did not recognize the following symptoms: {', '.join(unknown_symptoms)}\n"
        
        return response

    def get_disease_info(self, disease_key):
        """Gets information for a single disease from the loaded database."""
        if not self.disease_db:
            return "ERROR: The disease database is not loaded."

        if disease_key in self.disease_db:
            disease = self.disease_db[disease_key]
            response = f"**{disease['display_name']}**\n"
            response = f"Description: {disease['description']}\n"
            response += f"Suggested Care: {disease['care']}\n\n"
        else:
            response = f"No information available for '{disease_key.replace('_', ' ')}'. Please check the spelling."
        return response


if __name__ == "__main__":
    app = MedicalChatBot()
    app.mainloop()
