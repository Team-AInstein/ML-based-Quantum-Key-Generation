# Testing Guide - Quantum-Secured Chatbot

Complete testing procedures to verify all components work correctly.

---

## 🧪 Test Suite Overview

| Test | Type | Duration | Purpose |
|------|------|----------|---------|
| Test 1 | Installation | 2 min | Verify dependencies installed |
| Test 2 | Server Startup | 1 min | Verify server starts correctly |
| Test 3 | Web UI Access | 1 min | Verify browser access works |
| Test 4 | Single Room Chat | 3 min | Verify 2-user communication |
| Test 5 | Multi-Room Support | 3 min | Verify room isolation |
| Test 6 | Quantum Key Generation | 2 min | Verify BB84 integration |
| Test 7 | Message Encryption | 2 min | Verify encryption/decryption |
| Test 8 | CLI Client | 2 min | Verify terminal client |
| Test 9 | Network Access | 5 min | Verify cross-device chat |
| Test 10 | Stress Test | 5 min | Verify concurrent users |

**Total Time: ~25 minutes for complete validation**

---

## 📋 Test 1: Installation Verification

### Objective
Verify all dependencies installed correctly

### Steps

```powershell
# Navigate to frontend
cd C:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend

# Run installation
pip install -r requirements.txt
```

### Expected Results

```
Collecting flask==2.3.2
  Downloading flask-2.3.2-py3-none-any.whl (101 kB)
  Installing collected packages: flask, flask-socketio, ...
Successfully installed flask-2.3.2
Successfully installed flask-socketio-5.3.4
Successfully installed python-socketio-5.9.0
Successfully installed colorama-0.4.6
```

### Pass Criteria
- ✅ All packages installed without errors
- ✅ No dependency conflicts
- ✅ Pip shows "Successfully installed"

### If Test Fails

```bash
# Try individual installation
pip install flask==2.3.2
pip install flask-socketio==5.3.4
pip install python-socketio==5.9.0
pip install colorama==0.4.6
```

---

## 📋 Test 2: Server Startup

### Objective
Verify server starts without errors

### Steps

```powershell
# Start server
python server.py
```

### Expected Output

```
======================================================================
QUANTUM-SECURED CHATBOT SERVER
======================================================================
Starting server on 0.0.0.0:5000
Access from browser: http://localhost:5000
Access from network: http://<your-ip>:5000

Encryption: All messages secured with quantum keys (BB84)
======================================================================
 * Serving Flask app 'server'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

### Pass Criteria
- ✅ Server starts without errors
- ✅ Listening on port 5000
- ✅ Shows access URLs
- ✅ No import errors

### If Test Fails

**Error: "ModuleNotFoundError: No module named 'bb84_wrapper'"**

Solution: Check path in `quantum_key_manager.py`:
```python
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 
    'Final', 'Zeenats_Debug', 'ML-based-QKD-using-DeepQN', 'RL'
))
```

**Error: "Address already in use"**

Solution: Kill process on port 5000 and restart

---

## 📋 Test 3: Web UI Access

### Objective
Verify web browser can access interface

### Prerequisites
- Server running (Test 2 passed)

### Steps

1. Open browser (Chrome, Firefox, Edge)
2. Navigate to: `http://localhost:5000`
3. Wait for page to load
4. Observe interface

### Expected Results

You should see:
- [ ] Chat interface loads
- [ ] Sidebar on left with input fields
- [ ] Main chat area on right
- [ ] "Join Chat" button visible
- [ ] Username input field
- [ ] Room name input field
- [ ] No JavaScript errors in console

### Pass Criteria
- ✅ Page loads without errors
- ✅ All UI elements visible
- ✅ Responsive layout
- ✅ No console errors (press F12 to check)

### If Test Fails

**Page shows "Cannot GET /"**
- Server not running, restart with `python server.py`

**Page loads but looks broken**
- Check browser console (F12)
- Clear browser cache (Ctrl+Shift+Delete)

---

## 📋 Test 4: Single Room Chat (Web Interface)

### Objective
Verify two users can chat in same room with encryption

### Prerequisites
- Server running
- Test 3 passed

### Steps

1. **User 1 (Alice) - Browser Tab 1:**
   - Go to http://localhost:5000
   - Username: "Alice"
   - Room: "TestRoom"
   - Click "Join Chat"
   - Wait for message "Quantum key generated"

2. **User 2 (Bob) - Browser Tab 2:**
   - Go to http://localhost:5000
   - Username: "Bob"
   - Room: "TestRoom" (same room!)
   - Click "Join Chat"

3. **Alice sends message:**
   - Type: "Hello Bob!"
   - Click Send
   - Observe message appears in chat

4. **Bob receives & replies:**
   - Message should appear in Bob's chat
   - Bob types: "Hi Alice!"
   - Click Send

5. **Alice receives:**
   - Bob's message appears in Alice's chat

### Expected Results

**Alice's Screen:**
```
[12:34:56] System: Quantum key generated for room TestRoom
[12:34:58] ✓ Alice: aGVsbG8gYm9i... (your encrypted message)
[12:35:00] ✓ Bob: aGkgYWxpY2U=... (Bob's encrypted reply)
```

**Bob's Screen:**
```
[12:34:57] System: Quantum key generated for room TestRoom
[12:34:58] ✓ Alice: aGVsbG8gYm9i...
[12:35:00] ✓ Bob: aGkgYWxpY2U=... (your encrypted message)
```

### Pass Criteria
- ✅ Quantum key generated in ~2 seconds
- ✅ Messages appear encrypted
- ✅ Both users see same messages
- ✅ Real-time delivery
- ✅ No errors in console

### If Test Fails

**Quantum key generation stuck:**
- Check BB84 modules are accessible
- Server logs should show key generation status

**Messages not appearing:**
- Check browser console for errors
- Verify both in same room name
- Refresh page and rejoin

**Messages appearing as plain text:**
- Encryption disabled (expected in debug mode)
- Check quantum_encryption.py is being called

---

## 📋 Test 5: Multi-Room Support

### Objective
Verify rooms are isolated (different keys)

### Prerequisites
- Server running
- Test 4 passed

### Steps

1. **Create Room 1:**
   - Tab 1: Alice, Room: "General"
   - Tab 2: Bob, Room: "General"
   - They chat (Key generated for "General")

2. **Create Room 2 (Different Window):**
   - Tab 3: Charlie, Room: "Private"
   - Tab 4: Diana, Room: "Private"
   - They chat (Different key for "Private")

3. **Verify Isolation:**
   - Charlie sends message to Diana
   - Message should NOT appear in Alice/Bob's chat
   - Charlie cannot see Alice/Bob's messages

4. **Server Logs:**
   - Should show 2 keys generated
   - One for "General"
   - One for "Private"

### Expected Results

**Server output shows:**
```
Room 'General' quantum key generated! (Key #1)
Room 'Private' quantum key generated! (Key #2)
```

**Chat isolation:**
- General room: Only Alice/Bob's messages
- Private room: Only Charlie/Diana's messages
- NO cross-room message leakage

### Pass Criteria
- ✅ Different keys for different rooms
- ✅ Messages not visible across rooms
- ✅ Each room has isolated user list
- ✅ Server logs show multiple keys

### If Test Fails

**Messages appear in wrong room:**
- Check socket.io join logic in server.py
- Verify room names are different

**Same key used for both rooms:**
- Check quantum_key_manager.py `get_key()` method
- Should generate new key per room

---

## 📋 Test 6: Quantum Key Generation

### Objective
Verify BB84 protocol generates secure keys

### Prerequisites
- Server running
- Test 2 passed

### Steps

1. **Check Server Logs:**
   - Start server with DEBUG=True
   - Join a room
   - Observe server output

2. **Expected Key Generation Process:**
   - BB84 generates 512 qubits
   - Sifting reduces to ~25% (128 bits)
   - Privacy amplification reduces to ~3% (16 bits)
   - QBER calculated (~0.95%)

3. **Verify Security:**
   - QBER < 0.05 indicates secure channel
   - No Eve eavesdropping detected
   - Key marked as "SECURE"

### Expected Output in Server Logs

```
[2024-01-15 12:34:56] Room 'TestRoom' generating quantum key...
[2024-01-15 12:34:58] BB84 Protocol Results:
  - Input: 512 qubits
  - Sifted: 128 bits (25%)
  - Final: 16 bits (3%)
  - QBER: 0.95%
  - Eve Detected: NO
  - Status: ✓ SECURE
```

### Pass Criteria
- ✅ QBER between 0.5% - 2.0%
- ✅ QBER < 0.05 threshold met
- ✅ Eve not detected
- ✅ Key generation completes in <3 seconds
- ✅ Final key stored in memory

### If Test Fails

**QBER very high (>5%):**
- Indicates potential eavesdropping or channel noise too high
- Try restarting server

**QBER always 0:**
- Channel error rate not implemented
- Check if fix applied (TEST THIS SEPARATELY)

**Key generation fails:**
- BB84 module not found
- Check sys.path in quantum_key_manager.py

---

## 📋 Test 7: Message Encryption Verification

### Objective
Verify messages are encrypted with quantum keys

### Steps

1. **Intercept Encrypted Message:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Send message "Hello World"
   - Check the WebSocket data

2. **Expected Format:**
   - Raw data: Base64-encoded bytes
   - NOT plaintext "Hello World"
   - Example: `aGVsbG8gd29ybGQ=` (base64 of "hello world")

3. **Decryption Verification:**
   - Message appears as plaintext in UI
   - But encrypted in WebSocket traffic
   - Encryption/decryption transparent to user

### Pass Criteria
- ✅ WebSocket shows encrypted data
- ✅ NOT plaintext message
- ✅ Receiver sees decrypted message
- ✅ No encryption errors

### Verification Code

```python
# Test encryption locally
from quantum_encryption import MessageCrypto
from quantum_key_manager import QuantumKeyManager

qkm = QuantumKeyManager()
key = qkm.generate_quantum_key("test_session")

crypto = MessageCrypto(key)
encrypted = crypto.encrypt("Hello World")
decrypted = crypto.decrypt(encrypted)

print(f"Original: Hello World")
print(f"Encrypted: {encrypted}")
print(f"Decrypted: {decrypted}")
```

### Expected Output
```
Original: Hello World
Encrypted: aGVsbG8gd29ybGQ= [truncated base64]
Decrypted: Hello World
```

---

## 📋 Test 8: CLI Client

### Objective
Verify command-line client works

### Prerequisites
- Server running (separate terminal)

### Steps

**Terminal 1: Start Server**
```powershell
python server.py
```

**Terminal 2: Start CLI Client - User 1**
```powershell
python client.py -u Alice -r General -s http://localhost:5000
```

**Terminal 3: Start CLI Client - User 2**
```powershell
python client.py -u Bob -r General -s http://localhost:5000
```

### Expected Results

**Alice's Terminal:**
```
Connected to server!
Joined room 'General' as 'Alice'
Waiting for quantum key generation...
✓ Quantum key generated! Key length: 16 bits
Alice> Hello Bob!
Alice> /stats
```

**Bob's Terminal:**
```
Connected to server!
Joined room 'General' as 'Bob'
✓ Quantum key generated! Key length: 16 bits
Bob> (receives Alice's message)
Bob> Hi Alice!
```

### Commands to Test

```
/stats  - Show statistics
/help   - Show help
/quit   - Exit
```

### Pass Criteria
- ✅ Client connects to server
- ✅ Joins room successfully
- ✅ Quantum key generated
- ✅ Messages sent/received
- ✅ Commands work
- ✅ Can quit cleanly

### If Test Fails

**Connection refused:**
- Server not running
- Check port number
- Verify firewall

**Module not found:**
- Check python environment
- Ensure installed dependencies

---

## 📋 Test 9: Network Access (Cross-Device)

### Objective
Verify two users on different machines can chat

### Prerequisites
- Both machines on same WiFi/network
- Server running on one machine

### Steps

**Machine A (Server):**
1. Find IP: `ipconfig` → IPv4 Address (e.g., 192.168.1.100)
2. Start server: `python server.py`
3. Keep terminal open

**Machine B (Client):**
1. Open browser
2. Go to: `http://192.168.1.100:5000`
3. Join room "General"

**Machine A (Optional - Web Client):**
1. Also go to `http://192.168.1.100:5000` (or localhost)
2. Join same room "General"

### Expected Results

- Machine B can access chat interface
- Can join room successfully
- Can see quantum key generation message
- Can send/receive messages with Machine A
- Messages encrypted with shared quantum key

### Pass Criteria
- ✅ Cross-machine connection works
- ✅ Same room messages visible
- ✅ Real-time message delivery
- ✅ No network errors

### If Test Fails

**Cannot connect to IP:**
- Wrong IP address (check `ipconfig`)
- Firewall blocking port 5000
- Machines not on same network
- Try using hostname instead of IP

**Connection times out:**
- Verify server is running
- Check firewall allows port 5000
- Try `ping` to verify network connectivity

---

## 📋 Test 10: Stress Test (Concurrent Users)

### Objective
Verify system handles multiple simultaneous users

### Steps

1. **Create Multiple Browser Tabs:**
   - Tab 1: Alice in "General"
   - Tab 2: Bob in "General"
   - Tab 3: Charlie in "General"
   - Tab 4: Diana in "General"

2. **Send Messages Rapidly:**
   - Alice: 5 messages
   - Bob: 5 messages
   - Charlie: 5 messages
   - Diana: 5 messages
   - Total: 20 messages in 10 seconds

3. **Verify Message Order:**
   - All 20 messages received
   - Messages in correct order (by timestamp)
   - No messages lost

4. **Check Server:**
   - No errors in terminal
   - CPU usage reasonable
   - Memory usage stable

### Expected Results

```
All 4 users connected to General room
Sending 20 messages total
Expected: All 20 messages delivered in correct order
Time: <5 seconds
Server: No errors, stable performance
```

### Pass Criteria
- ✅ All users connected simultaneously
- ✅ No message loss
- ✅ Messages in order
- ✅ Server remains stable
- ✅ No crashes or errors

### Load Test Variations

**Light Load:**
- 2 users, 10 messages each

**Medium Load:**
- 4 users, 50 messages total

**Heavy Load:**
- 10 users, 100 messages total

---

## 🎯 Test Execution Checklist

Use this checklist to track test progress:

- [ ] Test 1: Installation
- [ ] Test 2: Server Startup
- [ ] Test 3: Web UI Access
- [ ] Test 4: Single Room Chat
- [ ] Test 5: Multi-Room Support
- [ ] Test 6: Quantum Key Generation
- [ ] Test 7: Message Encryption
- [ ] Test 8: CLI Client
- [ ] Test 9: Network Access
- [ ] Test 10: Stress Test

---

## 📊 Test Results Template

**Date:** _______________  
**Tester:** _______________  
**Environment:** Windows / Linux / Mac  
**Python Version:** _______________  

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Installation | PASS / FAIL | |
| 2 | Server Startup | PASS / FAIL | |
| 3 | Web UI Access | PASS / FAIL | |
| 4 | Single Room Chat | PASS / FAIL | |
| 5 | Multi-Room Support | PASS / FAIL | |
| 6 | Quantum Key Generation | PASS / FAIL | |
| 7 | Message Encryption | PASS / FAIL | |
| 8 | CLI Client | PASS / FAIL | |
| 9 | Network Access | PASS / FAIL | |
| 10 | Stress Test | PASS / FAIL | |

**Overall Result:** PASS / FAIL

**Issues Found:**
1. ___________________________________
2. ___________________________________
3. ___________________________________

---

## 🐛 Debugging Tips

### Enable Verbose Logging

Edit `server.py`:
```python
DEBUG = True  # Show detailed logs
```

### Check WebSocket Traffic

Open browser DevTools (F12):
1. Network tab
2. Filter by "WS" (WebSocket)
3. See message encryption in real-time

### Test Encryption Locally

```python
python
>>> from quantum_encryption import MessageCrypto
>>> from quantum_key_manager import QuantumKeyManager
>>> qkm = QuantumKeyManager()
>>> key = qkm.generate_quantum_key("test")
>>> crypto = MessageCrypto(key)
>>> encrypted = crypto.encrypt("Test message")
>>> print(crypto.decrypt(encrypted))
Test message
```

### Monitor Server Output

Keep server terminal visible to see:
- New connections
- Key generation
- Errors and warnings

---

## ✅ All Tests Passed!

If all tests passed:

1. System is working correctly
2. Quantum keys generating properly
3. Encryption/decryption functioning
4. Multi-user support verified
5. Network access operational
6. Ready for deployment!

**Congratulations! Your quantum-secured chatbot is ready!** 🎉⚛️🔐

---

## 📞 Support

If tests fail, check:

1. **Installation:** Run pip install again
2. **Server:** Restart server
3. **Firewall:** Allow port 5000
4. **Paths:** Verify BB84 module paths
5. **Network:** Check device connectivity

See README.md for more troubleshooting!
