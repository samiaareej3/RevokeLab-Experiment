import os
import asyncio
import ssl
import json
import argparse
import httpx
import websockets
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("REVOKELAB_BASE_URL")
ALICE_USERNAME = os.getenv("ALICE_USERNAME")
ALICE_PASSWORD = os.getenv("ALICE_PASSWORD")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

PROJECT_ID = 1
ALICE_USER_ID = 2
RESULTS_DIR = "results"


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def generate_message_code():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"DEMO-{timestamp}"


def save_result(result):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    filename = (
        f"experiment_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.json"
    )

    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(f"\n💾 Result saved to: {filepath}")


def restore_alice():
    print("\n🔓 Restoring Alice's access...")

    with httpx.Client(
        base_url=BASE_URL,
        follow_redirects=True,
        timeout=30.0
    ) as client:

        response = client.post(
            "/auth/login",
            data={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
            },
        )

        response.raise_for_status()

        response = client.post(
            f"/projects/{PROJECT_ID}/members/{ALICE_USER_ID}/grant"
        )

        response.raise_for_status()

        print("✅ Alice's access restored")


async def run_experiment(wait_seconds):

    result = {
        "experiment": "RevokeLab",
        "authorization_mode": "connection-only",
        "project_id": PROJECT_ID,
        "wait_seconds": wait_seconds,
        "connection_time": None,
        "revocation_time": None,
        "message_time": None,
        "received_time": None,
        "message_code": None,
        "message_received": False,
        "result": None,
    }

    try:
        print("=" * 55)
        print("RevokeLab Experiment")
        print("=" * 55)

        print(f"\n⏱️ Wait time: {wait_seconds} seconds")

        # -----------------------------------------
        # STEP 1: Login as Alice
        # -----------------------------------------

        print("\n🔐 Step 1: Logging in as Alice...")

        with httpx.Client(
            base_url=BASE_URL,
            follow_redirects=True,
            timeout=30.0
        ) as alice_client:

            response = alice_client.post(
                "/auth/login",
                data={
                    "username": ALICE_USERNAME,
                    "password": ALICE_PASSWORD,
                },
            )

            response.raise_for_status()

            print("✅ Alice logged in")

            response = alice_client.get("/auth/me")
            response.raise_for_status()

            print("👤 Current user:", response.json())

            # -----------------------------------------
            # STEP 2: Open WebSocket
            # -----------------------------------------

            print("\n🔌 Step 2: Opening Alice's WebSocket...")

            cookies = alice_client.cookies

            cookie_header = "; ".join(
                f"{cookie.name}={cookie.value}"
                for cookie in cookies.jar
            )

            ws_url = (
                BASE_URL
                .replace("https://", "wss://")
                .replace("http://", "ws://")
            )

            ws_url = (
                f"{ws_url}/ws/connection-only/projects/{PROJECT_ID}"
            )

            print("WebSocket URL:", ws_url)

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(
                ws_url,
                additional_headers={
                    "Cookie": cookie_header
                },
                ssl=ssl_context,
            ) as websocket:

                connection_time = now_utc()
                result["connection_time"] = connection_time

                print("✅ WebSocket connected!")
                print("🕐 Connection time:", connection_time)

                connected_message = await websocket.recv()

                print("📩 WebSocket response:", connected_message)

                # -----------------------------------------
                # STEP 3: Revoke Alice
                # -----------------------------------------

                print("\n🚫 Step 3: Revoking Alice...")

                with httpx.Client(
                    base_url=BASE_URL,
                    follow_redirects=True,
                    timeout=30.0
                ) as admin_client:

                    response = admin_client.post(
                        "/auth/login",
                        data={
                            "username": ADMIN_USERNAME,
                            "password": ADMIN_PASSWORD,
                        },
                    )

                    response.raise_for_status()

                    print("✅ Admin logged in")

                    response = admin_client.post(
                        f"/projects/{PROJECT_ID}/members/{ALICE_USER_ID}/revoke"
                    )

                    response.raise_for_status()

                    revocation_time = now_utc()

                    result["revocation_time"] = revocation_time

                    print("Revoke response:", response.json())
                    print("✅ Alice revoked")
                    print("🕐 Revocation time:", revocation_time)

                    # -----------------------------------------
                    # STEP 4: Wait
                    # -----------------------------------------

                    print(
                        f"\n⏳ Waiting {wait_seconds} seconds "
                        "after revocation..."
                    )

                    await asyncio.sleep(wait_seconds)

                    # -----------------------------------------
                    # STEP 5: Create new message
                    # -----------------------------------------

                    message_code = generate_message_code()

                    result["message_code"] = message_code

                    print(
                        f"\n📨 Step 5: Creating {message_code}..."
                    )

                    response = admin_client.post(
                        f"/projects/{PROJECT_ID}/messages",
                        json={
                            "message_code": message_code,
                            "content": "Post-revocation experiment message",
                        },
                    )

                    response.raise_for_status()

                    message_time = now_utc()

                    result["message_time"] = message_time

                    print("Message response:", response.json())
                    print(f"✅ {message_code} created")
                    print("🕐 Message time:", message_time)

                # -----------------------------------------
                # STEP 6: Check WebSocket
                # -----------------------------------------

                print(
                    "\n👀 Step 6: Checking Alice's "
                    "existing WebSocket..."
                )

                try:

                    received = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5
                    )

                    received_time = now_utc()

                    result["received_time"] = received_time

                    print("📩 Received:", received)
                    print("🕐 Received time:", received_time)

                    if message_code in received:

                        result["message_received"] = True
                        result["result"] = "FAIL"

                        print(
                            "\n🚨 RESULT: MESSAGE RECEIVED "
                            "AFTER REVOCATION"
                        )

                    else:

                        result["result"] = "INCONCLUSIVE"

                        print(
                            "\n⚠️ Received a message, "
                            "but it was not the test message."
                        )

                except asyncio.TimeoutError:

                    result["message_received"] = False
                    result["result"] = "PASS"

                    print(
                        "\n✅ RESULT: NO MESSAGE RECEIVED "
                        "AFTER REVOCATION"
                    )

    finally:

        try:
            restore_alice()
        finally:
            save_result(result)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Run the RevokeLab revocation experiment."
    )

    parser.add_argument(
        "--wait",
        type=float,
        required=True,
        help="Seconds to wait after revocation before creating the message.",
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    asyncio.run(
        run_experiment(args.wait)
    )