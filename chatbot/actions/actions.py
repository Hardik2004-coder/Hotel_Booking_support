import sqlite3
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'owner.db')


class ActionSearchHotelByName(Action):
    def name(self) -> Text:
        return "action_search_hotel_by_name"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hotel_name = tracker.get_slot("hotel_name")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM hotels WHERE hotel_name LIKE ?", (f"%{hotel_name}%",))
        hotel = c.fetchone()

        if hotel:
            owner_email = hotel[7]
            c.execute("SELECT * FROM owners WHERE email = ?", (owner_email,))
            owner = c.fetchone()

            dispatcher.utter_message(text="Found the Hotel!")
            dispatcher.utter_message(
    text="Hotel Details:\n\n"
         f"🏨 Hotel Name: {hotel[1]},"
         f"🛏️ Rooms: {hotel[2]},"
         f"📍 Location: {hotel[3]},"
         f"📬 Address: {hotel[4]},"
         f"📶 WiFi: {'Yes' if hotel[5] else 'No'},"
         f"🚗 Parking: {'Yes' if hotel[6] else 'No'},"
         f"👤 Owner: {owner[1]},"
         f"📞 Contact: {owner[3]},"
         f"✉️ Email: {owner[2]}"
)
        else:
            dispatcher.utter_message(response="utter_no_hotel_found")

        conn.close()
        return []


class ActionSearchHotelByLocation(Action):
    def name(self) -> Text:
        return "action_search_hotel_by_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM hotels WHERE location LIKE ?", (f"%{location}%",))
        hotels = c.fetchall()

        if hotels:
            dispatcher.utter_message(text="Found the Hotel(s)!")
            for hotel in hotels:
                c.execute("SELECT * FROM owners WHERE email = ?", (hotel[7],))
                owner = c.fetchone()
                dispatcher.utter_message(
    text="Hotel Details:\n\n"
         f"🏨 Hotel Name: {hotel[1]},"
         f"🛏️ Rooms: {hotel[2]},"
         f"📍 Location: {hotel[3]},"
         f"📬 Address: {hotel[4]},"
         f"📶 WiFi: {'Yes' if hotel[5] else 'No'},"
         f"🚗 Parking: {'Yes' if hotel[6] else 'No'},"
         f"👤 Owner: {owner[1]},"
         f"📞 Contact: {owner[3]},"
         f"✉️ Email: {owner[2]}"
)
        else:
            dispatcher.utter_message(response="utter_no_location_found")

        conn.close()
        return []
