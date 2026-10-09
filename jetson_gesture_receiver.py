import socket
import json
from Arm_Lib import Arm_Device
import time

Arm = Arm_Device()

HOST = '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("🔴 Waiting for laptop connection on port 5000...")
print("Keep this terminal open!")

conn, addr = server.accept()
print(f"✅ Connected by {addr}")

try:
    buffer = ""
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            try:
                cmd = json.loads(line)
                base     = cmd.get("base", 90)
                shoulder = cmd.get("shoulder", 90)
                elbow    = cmd.get("elbow", 90)
                wrist    = cmd.get("wrist", 90)
                gripper  = cmd.get("gripper", 90)

                Arm.Arm_serial_servo_write(1, base,     1200)
                Arm.Arm_serial_servo_write(2, shoulder, 1100)
                Arm.Arm_serial_servo_write(3, elbow,    1100)
                Arm.Arm_serial_servo_write(4, wrist,    1000)
                Arm.Arm_serial_servo_write(6, gripper,   800)

                print(f"Base:{base:3d}  Shoulder:{shoulder:3d}  Elbow:{elbow:3d}  Wrist:{wrist:3d}  Gripper:{gripper:3d}")
            except Exception as e:
                print("Parse error:", e)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")
finally:
    conn.close()
    server.close()
    print("Returning arm to home position...")
    Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 90, 1500)
    time.sleep(1.6)
    print("Done.")
