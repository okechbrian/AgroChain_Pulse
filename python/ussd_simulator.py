"""
USSD Session Simulator - Mimics MTN/Airtel USSD Gateway
"""

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class USSDMenuLevel(Enum):
    MAIN = 1
    REGISTER = 2
    CHECK_BALANCE = 3
    YPS_SCORE = 4
    TOKEN_MENU = 5
    REDEEM_ENERGY = 6


@dataclass
class USSDSession:
    session_id: str
    phone_number: str
    current_menu: USSDMenuLevel = USSDMenuLevel.MAIN
    user_data: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class USSDSimulator:
    """
    Simulates USSD gateway behavior for MTN/Airtel Uganda
    """

    def __init__(self):
        self.sessions: Dict[str, USSDSession] = {}
        self.response_templates = self._load_response_templates()

    def _load_response_templates(self) -> Dict:
        return {
            USSDMenuLevel.MAIN: "CON Welcome to AgroChain Pulse\n1. Register Farm\n2. Check YPS Score\n3. Energy Tokens\n4. Help\n\nEnter your choice:",
            USSDMenuLevel.REGISTER: "CON Enter your name:",
            USSDMenuLevel.CHECK_BALANCE: "CON Your Energy Credit Token Balance: {balance} kWh\n\n1. Back to Main Menu",
            USSDMenuLevel.YPS_SCORE: "CON Your Yield Probability Score: {yps}\n\nScore Interpretation:\n800-1000: Excellent - High creditworthy\n600-799: Good - Eligible for tokens\n400-599: Fair - Limited tokens\n0-399: Low - Build your score\n\n1. Back to Main Menu",
            USSDMenuLevel.TOKEN_MENU: "CON Energy Credit Tokens\n1. Redeem Energy\n2. View Transaction History\n3. Back",
            USSDMenuLevel.REDEEM_ENERGY: "CON Enter the pump node ID to redeem energy:",
        }

    def create_session(self, phone_number: str) -> USSDSession:
        session_id = f"USS{time.time():.0f}{hash(phone_number) % 10000}"
        session = USSDSession(session_id=session_id, phone_number=phone_number)
        self.sessions[session_id] = session
        return session

    def process_input(
        self,
        session_id: str,
        user_input: str,
        yps_score: Optional[int] = None,
        token_balance: Optional[float] = None,
    ) -> str:
        if session_id not in self.sessions:
            return "END Session expired. Dial *201# to start again."

        session = self.sessions[session_id]
        session.last_activity = datetime.now()

        menu = session.current_menu
        response = ""

        # Handle initial entry to main menu (user dials *201#)
        if menu == USSDMenuLevel.MAIN and not user_input.strip():
            return self.response_templates[USSDMenuLevel.MAIN]

        # Skip handlers when at main menu with no valid input
        if menu == USSDMenuLevel.MAIN:
            response = self._handle_main_menu(session, user_input)

        elif menu == USSDMenuLevel.REGISTER:
            response = self._handle_register(session, user_input)

        elif menu == USSDMenuLevel.CHECK_BALANCE:
            response = self._handle_check_balance(session, user_input)

        elif menu == USSDMenuLevel.YPS_SCORE:
            response = self._handle_yps_score(session, user_input, yps_score)

        elif menu == USSDMenuLevel.TOKEN_MENU:
            response = self._handle_token_menu(session, user_input)

        elif menu == USSDMenuLevel.REDEEM_ENERGY:
            response = self._handle_redeem_energy(session, user_input)

        return response

    def _handle_main_menu(self, session: USSDSession, user_input: str) -> str:
        choice = user_input.strip()

        if choice == "1":
            session.current_menu = USSDMenuLevel.REGISTER
            return self.response_templates[USSDMenuLevel.REGISTER]
        elif choice == "2":
            session.current_menu = USSDMenuLevel.YPS_SCORE
            return self.response_templates[USSDMenuLevel.YPS_SCORE]
        elif choice == "3":
            session.current_menu = USSDMenuLevel.TOKEN_MENU
            return self.response_templates[USSDMenuLevel.TOKEN_MENU]
        elif choice == "4":
            return "END AgroChain Pulse helps farmers get energy credit based on soil data. Dial *201# to start."
        else:
            return "END Invalid choice. Dial *201# to try again."

    def _handle_register(self, session: USSDSession, user_input: str) -> str:
        session.user_data["farmer_name"] = user_input.strip()
        session.current_menu = USSDMenuLevel.MAIN
        return "END Registration successful! Your farm has been linked. Dial *201# to check your YPS Score."

    def _handle_check_balance(self, session: USSDSession, user_input: str) -> str:
        if user_input == "1":
            session.current_menu = USSDMenuLevel.MAIN
            return self.response_templates[USSDMenuLevel.MAIN]
        balance = session.user_data.get("token_balance", 0)
        template = self.response_templates[USSDMenuLevel.CHECK_BALANCE]
        return template.format(balance=balance)

    def _handle_yps_score(
        self, session: USSDSession, user_input: str, yps_score: Optional[int] = None
    ) -> str:
        choice = user_input.strip()

        if choice == "1":
            session.current_menu = USSDMenuLevel.MAIN
            return self.response_templates[USSDMenuLevel.MAIN]

        yps = (
            yps_score
            if yps_score is not None
            else session.user_data.get("yps_score", 750)
        )
        template = self.response_templates[USSDMenuLevel.YPS_SCORE]
        return template.format(yps=yps)

    def _handle_token_menu(self, session: USSDSession, user_input: str) -> str:
        choice = user_input.strip()

        if choice == "1":
            session.current_menu = USSDMenuLevel.REDEEM_ENERGY
            return self.response_templates[USSDMenuLevel.REDEEM_ENERGY]
        elif choice == "2":
            return "END Transaction history coming soon!"
        elif choice == "3":
            session.current_menu = USSDMenuLevel.MAIN
            return self.response_templates[USSDMenuLevel.MAIN]
        else:
            return "END Invalid choice."

    def _handle_redeem_energy(self, session: USSDSession, user_input: str) -> str:
        session.current_menu = USSDMenuLevel.MAIN
        return f"END Successfully redeemed energy at pump {user_input}. Thank you for using AgroChain Pulse!"

    def get_session(self, session_id: str) -> Optional[USSDSession]:
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> str:
        if session_id in self.sessions:
            del self.sessions[session_id]
        return "END Session ended. Thank you for using AgroChain Pulse!"


def demo():
    simulator = USSDSimulator()

    print("=" * 60)
    print("USSD SIMULATOR DEMO - MTN/Airtel Uganda Gateway")
    print("=" * 60)

    session = simulator.create_session("+256771234567")
    print(f"\n[New Session] Session ID: {session.session_id}")
    print(f"[Phone]: {session.phone_number}")

    print("\n--- Step 1: User dials *201# (enters main menu) ---")
    response = simulator.process_input(session.session_id, "")
    print(f"[Response]:\n{response}")

    print("\n--- Step 2: User selects '1' to Register ---")
    response = simulator.process_input(session.session_id, "1")
    print(f"[Response]: {response}")

    print("\n--- Step 3: User enters name 'John Okello' ---")
    response = simulator.process_input(session.session_id, "John Okello")
    print(f"[Response]: {response}")

    session2 = simulator.create_session("+256772345678")
    print(f"\n[New Session] Session ID: {session2.session_id}")

    print("\n--- Step 4: User dials *201# and selects '2' for YPS ---")
    response = simulator.process_input(session2.session_id, "")  # main menu
    print(f"[Response]:\n{response}")
    response = simulator.process_input(session2.session_id, "2", yps_score=750)
    print(f"[Response]:\n{response}")

    print("\n--- Step 5: User goes back and selects '3' for Tokens ---")
    response = simulator.process_input(session2.session_id, "1")  # back to main
    print(f"[Response]:\n{response}")
    response = simulator.process_input(session2.session_id, "3")
    print(f"[Response]:\n{response}")

    print("\n--- Step 6: User selects '1' to Redeem Energy ---")
    response = simulator.process_input(session2.session_id, "1")
    print(f"[Response]: {response}")

    print("\n--- Step 7: User enters pump node ID 'PN001' ---")
    response = simulator.process_input(session2.session_id, "PN001")
    print(f"[Response]: {response}")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
