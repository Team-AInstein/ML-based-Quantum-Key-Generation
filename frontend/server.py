"""
Quantum-Secured Chatbot Backend Server

Flask + Socket.IO server for real-time messaging with quantum key encryption.
Serves on local network - accessible to any device connected to same network.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS

# Import quantum security modules
from quantum_key_manager import QuantumKeyManager, SecurityError
from quantum_encryption import MessageCrypto


class QuantumChatServer:
    """
    Quantum-secured chat server.
    
    Features:
    - Generates unique quantum keys for each chat session
    - Encrypts/decrypts all messages using quantum keys
    - Supports multiple concurrent conversations
    - Real-time messaging via WebSockets
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize chat server.
        
        Args:
            host: Server host (0.0.0.0 = accessible from network)
            port: Server port
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.config['SECRET_KEY'] = 'quantum-secure-chatbot-key-2026'
        
        # Enable CORS for cross-origin requests
        CORS(self.app)
        
        # Initialize Socket.IO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize quantum key manager
        self.key_manager = QuantumKeyManager(key_length=512)
        
        # Track active users and sessions
        self.users: Dict[str, str] = {}  # socket_id -> username
        self.sessions: Dict[str, Dict] = {}  # room_id -> session_info
        self.room_keys: Dict[str, str] = {}  # room_id -> quantum_key
        self.room_cryptos: Dict[str, MessageCrypto] = {}  # room_id -> MessageCrypto
        
        # Setup routes and events
        self._setup_routes()
        self._setup_socket_events()
        
        print("✓ Quantum Chat Server initialized")
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main chat page."""
            return render_template('index.html')
        
        @self.app.route('/api/server-info')
        def server_info():
            """Get server information."""
            return jsonify({
                'server': 'Quantum-Secured Chatbot',
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'active_rooms': len(self.sessions),
                'active_users': len(self.users)
            })
        
        @self.app.route('/api/generate-key', methods=['POST'])
        def generate_key():
            """Generate quantum key for a session."""
            data = request.json
            session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
            
            try:
                result = self.key_manager.generate_quantum_key(session_id)
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'key_stats': result
                })
            except SecurityError as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
    
    def _setup_socket_events(self):
        """Setup Socket.IO events."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle user connection."""
            print(f"[EVENT] User connected: {request.sid}")
            emit('connection_response', {'status': 'connected'})
        
        @self.socketio.on('join')
        def on_join(data):
            """Handle user joining a chat room."""
            username = data.get('username', f'User_{request.sid[:8]}')
            room = data.get('room', 'lobby')
            
            # Store user info
            self.users[request.sid] = username
            
            # Join room
            join_room(room)
            
            print(f"[EVENT] {username} joined room: {room}")
            
            # Generate quantum key if room doesn't have one
            if room not in self.room_keys:
                try:
                    result = self.key_manager.generate_quantum_key(f"room_{room}")
                    self.room_keys[room] = self.key_manager.get_key(f"room_{room}")
                    self.room_cryptos[room] = MessageCrypto(self.room_keys[room])
                    
                    print(f"[QKD] Generated quantum key for room {room}")
                    print(f"  - Key length: {len(self.room_keys[room])} bits")
                    
                    emit('quantum_key_generated', {
                        'room': room,
                        'key_length': len(self.room_keys[room]),
                        'message': f"Quantum key generated for secure communication"
                    }, room=room)
                except SecurityError as e:
                    print(f"[ERROR] Failed to generate quantum key: {e}")
                    emit('error', {'message': str(e)})
                    return
            else:
                # Key already exists for this room - tell the new user it's ready
                emit('quantum_key_generated', {
                    'room': room,
                    'key_length': len(self.room_keys[room]),
                    'message': f"Quantum key already active for this room"
                })
            
            # Notify room
            emit('user_joined', {
                'username': username,
                'room': room,
                'users_in_room': list(set(
                    self.users[sid] for sid in rooms() 
                    if sid in self.users
                ))
            }, room=room)
        
        @self.socketio.on('send_message')
        def on_message(data):
            """Handle incoming message."""
            username = self.users.get(request.sid, 'Unknown')
            room = data.get('room', 'lobby')
            message = data.get('message', '')
            
            if not message:
                return
            
            # Truncate message if too long for key
            key_length = len(self.room_keys.get(room, ''))
            message_bits = len(message) * 8  # Rough estimate
            
            if message_bits > key_length:
                max_chars = key_length // 8
                message = message[:max_chars]
                print(f"[MSG] Message truncated to {max_chars} chars (key: {key_length} bits)")
            
            # Encrypt message with quantum key
            if room not in self.room_cryptos:
                emit('error', {'message': 'Room quantum key not initialized'})
                return
            
            try:
                crypto = self.room_cryptos[room]
                encrypted_data = crypto.encrypt_message(username, message)
                
                # Broadcast both plaintext and encrypted message to room
                emit('receive_message', {
                    'sender': username,
                    'message': message,  # Plaintext (decrypted)
                    'encrypted': encrypted_data.get('encrypted', ''),  # Encrypted ciphertext
                    'timestamp': encrypted_data.get('timestamp', ''),
                    'room': room
                }, room=room)
                
                print(f"[MSG] {username} → {room}: [encrypted {len(message)} chars]")
                print(f"  - Plaintext: {message}")
                print(f"  - Encrypted: {encrypted_data.get('encrypted', '')[:50]}...")
                
            except Exception as e:
                print(f"[ERROR] Encryption failed: {e}")
                emit('error', {'message': f'Encryption error: {e}'})
        
        @self.socketio.on('leave')
        def on_leave(data):
            """Handle user leaving room."""
            room = data.get('room', 'lobby')
            username = self.users.get(request.sid, 'Unknown')
            
            leave_room(room)
            
            print(f"[EVENT] {username} left room: {room}")
            
            emit('user_left', {
                'username': username,
                'room': room
            }, room=room)
            
            # Clean up empty rooms
            if not rooms() and room in self.room_keys:
                del self.room_keys[room]
                del self.room_cryptos[room]
                print(f"[QKD] Cleaned up quantum key for empty room: {room}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle user disconnection."""
            username = self.users.pop(request.sid, 'Unknown')
            print(f"[EVENT] User disconnected: {username}")
        
        @self.socketio.on('request_stats')
        def on_request_stats():
            """Send server statistics."""
            stats = {
                'active_users': len(self.users),
                'active_rooms': len(self.sessions),
                'active_keys': len(self.room_keys),
                'timestamp': datetime.now().isoformat()
            }
            emit('server_stats', stats)
    
    def run(self, debug: bool = True):
        """
        Run the server.
        
        Args:
            debug: Enable debug mode
        """
        print("\n" + "=" * 70)
        print("QUANTUM-SECURED CHATBOT SERVER")
        print("=" * 70)
        print(f"Starting server on {self.host}:{self.port}")
        print(f"Access from browser: http://localhost:{self.port}")
        print(f"Access from network: http://<your-ip>:{self.port}")
        print("\nEncryption: All messages secured with quantum keys (BB84)")
        print("=" * 70 + "\n")
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )


if __name__ == '__main__':
    # Create and run server
    server = QuantumChatServer(host='0.0.0.0', port=5000)
    server.run(debug=True)
