"""
Quantum-Secured Chatbot CLI Client

Terminal-based client for testing quantum-encrypted communication.
Can connect to any server on the network.
"""

import sys
import os
import json
import time
import threading
from datetime import datetime
from typing import Optional

try:
    import socketio
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip install python-socketio colorama")
    sys.exit(1)

# Import quantum modules
from quantum_key_manager import QuantumKeyManager
from quantum_encryption import MessageCrypto


class QuantumChatClient:
    """
    Terminal-based quantum chat client.
    
    Features:
    - Connect to quantum chat server
    - Real-time message encryption/decryption
    - Display quantum key information
    - Multi-user chat support
    """
    
    def __init__(self, server_url: str = 'http://localhost:5000'):
        """
        Initialize chat client.
        
        Args:
            server_url: Server URL (e.g., 'http://localhost:5000')
        """
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.username = ''
        self.room = ''
        self.crypto: Optional[MessageCrypto] = None
        self.message_count = 0
        
        # Setup event handlers
        self._setup_events()
    
    def _setup_events(self):
        """Setup Socket.IO event handlers."""
        
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            self._print(f"{Fore.GREEN}✓ Connected to server{Style.RESET_ALL}")
        
        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            self._print(f"{Fore.RED}✗ Disconnected from server{Style.RESET_ALL}")
        
        @self.sio.on('connection_response')
        def on_connection(data):
            self._print(f"Server: {data['status']}")
        
        @self.sio.on('quantum_key_generated')
        def on_key_generated(data):
            self._print(f"\n{Fore.CYAN}⚛️  Quantum Key Generated:{Style.RESET_ALL}")
            self._print(f"   Room: {data['room']}")
            self._print(f"   Key Size: {data['key_length']} bits")
            self._print(f"   Status: {data['message']}\n")
        
        @self.sio.on('user_joined')
        def on_user_joined(data):
            if data['username'] != self.username:
                self._print(f"{Fore.YELLOW}→ {data['username']} joined the chat{Style.RESET_ALL}")
                self._print(f"  Users in room: {', '.join(data['users_in_room'])}")
        
        @self.sio.on('user_left')
        def on_user_left(data):
            self._print(f"{Fore.YELLOW}← {data['username']} left the chat{Style.RESET_ALL}")
        
        @self.sio.on('receive_message')
        def on_message(data):
            sender = data['sender']
            encrypted = data['encrypted']
            timestamp = data['timestamp']
            
            # Try to decrypt if we have crypto key
            if self.crypto:
                try:
                    decrypted_data = self.crypto.decrypt_message(data)
                    message = decrypted_data['message']
                    status = "✓"
                except Exception as e:
                    message = f"[Decryption failed: {e}]"
                    status = "✗"
            else:
                message = "[Encrypted - no key]"
                status = "?"
            
            # Format timestamp
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
            
            # Print message
            if sender == self.username:
                self._print(f"{Fore.GREEN}{time_str} {status} You: {message}{Style.RESET_ALL}")
            else:
                self._print(f"{Fore.CYAN}{time_str} {status} {sender}: {message}{Style.RESET_ALL}")
            
            self.message_count += 1
        
        @self.sio.on('error')
        def on_error(data):
            self._print(f"{Fore.RED}⚠️  Error: {data['message']}{Style.RESET_ALL}")
    
    def connect(self) -> bool:
        """
        Connect to chat server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._print(f"Connecting to {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            self._print(f"{Fore.RED}Failed to connect: {e}{Style.RESET_ALL}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        if self.connected:
            self.sio.disconnect()
    
    def join_room(self, username: str, room: str = 'General'):
        """
        Join a chat room.
        
        Args:
            username: Your username
            room: Room name to join
        """
        self.username = username
        self.room = room
        
        self._print(f"Joining room '{room}' as {username}...")
        self.sio.emit('join', {
            'username': username,
            'room': room
        })
    
    def send_message(self, message: str):
        """
        Send an encrypted message.
        
        Args:
            message: Message text
        """
        if not self.connected:
            self._print(f"{Fore.RED}Not connected to server{Style.RESET_ALL}")
            return
        
        if not self.crypto:
            self._print(f"{Fore.RED}Quantum key not ready{Style.RESET_ALL}")
            return
        
        self.sio.emit('send_message', {
            'room': self.room,
            'message': message
        })
    
    def leave_room(self):
        """Leave current room."""
        self.sio.emit('leave', {
            'room': self.room
        })
        self.crypto = None
        self._print(f"Left room '{self.room}'")
    
    def show_stats(self):
        """Display client statistics."""
        self._print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        self._print(f"Client Statistics:")
        self._print(f"  Username: {self.username}")
        self._print(f"  Room: {self.room}")
        self._print(f"  Connected: {self.connected}")
        self._print(f"  Messages Sent: {self.message_count}")
        self._print(f"  Crypto Initialized: {self.crypto is not None}")
        self._print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    
    def _print(self, message: str):
        """Print with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def interactive_mode(self):
        """Run interactive chat mode."""
        self._print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        self._print(f"{Fore.MAGENTA}Quantum-Secured Chatbot - CLI Client{Style.RESET_ALL}")
        self._print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # Get server URL
        print(f"Server URL [{self.server_url}]: ", end='')
        url_input = input().strip()
        if url_input:
            self.server_url = url_input
        
        # Connect
        if not self.connect():
            return
        
        # Get username
        print(f"Username: ", end='')
        username = input().strip()
        if not username:
            username = f"User_{int(time.time()) % 10000}"
        
        # Get room
        print(f"Room [General]: ", end='')
        room = input().strip()
        if not room:
            room = 'General'
        
        # Join room
        self.join_room(username, room)
        time.sleep(1)
        
        # Generate quantum key
        self._print(f"{Fore.CYAN}Generating quantum key for secure communication...{Style.RESET_ALL}")
        try:
            km = QuantumKeyManager(key_length=512)
            key_result = km.generate_quantum_key(f"client_{username}_{room}")
            
            # Get the key
            key = km.get_key(f"client_{username}_{room}")
            if key:
                self.crypto = MessageCrypto(key)
                self._print(f"{Fore.GREEN}✓ Quantum key ready!{Style.RESET_ALL}")
                self._print(f"  Key length: {len(key)} bits")
                self._print(f"  Max message size: ~{self.crypto.encryptor.get_max_message_length()} chars\n")
            else:
                self._print(f"{Fore.RED}Failed to retrieve quantum key{Style.RESET_ALL}")
                return
        except Exception as e:
            self._print(f"{Fore.RED}Quantum key generation failed: {e}{Style.RESET_ALL}")
            return
        
        # Chat loop
        self._print(f"{Fore.GREEN}Ready to chat! Commands: /stats, /help, /quit{Style.RESET_ALL}\n")
        
        try:
            while True:
                message = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
                
                if not message:
                    continue
                
                # Handle commands
                if message.startswith('/'):
                    self._handle_command(message)
                    continue
                
                # Send message
                if len(message) > self.crypto.encryptor.get_max_message_length():
                    self._print(f"{Fore.YELLOW}Message too long (max {self.crypto.encryptor.get_max_message_length()} chars){Style.RESET_ALL}")
                    continue
                
                self.send_message(message)
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            self._print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            self.leave_room()
            self.disconnect()
    
    def _handle_command(self, command: str):
        """Handle CLI commands."""
        cmd = command.lower().strip('/')
        
        if cmd == 'stats':
            self.show_stats()
        elif cmd == 'help':
            self._print_help()
        elif cmd == 'quit':
            raise KeyboardInterrupt()
        else:
            self._print(f"Unknown command: {command}")
    
    def _print_help(self):
        """Print help message."""
        self._print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
        self._print(f"  /stats - Show client statistics")
        self._print(f"  /help  - Show this help message")
        self._print(f"  /quit  - Exit the chat\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Quantum-Secured Chatbot CLI Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client.py                           # Interactive mode (localhost)
  python client.py -s http://192.168.1.100:5000
  python client.py -u Alice -r "General"
        """
    )
    
    parser.add_argument('-s', '--server', 
                       default='http://localhost:5000',
                       help='Server URL (default: http://localhost:5000)')
    parser.add_argument('-u', '--username',
                       help='Username (interactive if not provided)')
    parser.add_argument('-r', '--room',
                       default='General',
                       help='Room name (default: General)')
    
    args = parser.parse_args()
    
    client = QuantumChatClient(server_url=args.server)
    
    if args.username:
        # Non-interactive mode
        if not client.connect():
            sys.exit(1)
        
        client.join_room(args.username, args.room)
        time.sleep(1)
        
        # Generate quantum key
        try:
            km = QuantumKeyManager(key_length=512)
            km.generate_quantum_key(f"client_{args.username}")
            key = km.get_key(f"client_{args.username}")
            if key:
                client.crypto = MessageCrypto(key)
                print(f"Connected as {args.username} in {args.room}")
                print(f"Quantum key ready ({len(key)} bits)")
            else:
                print("Failed to generate quantum key")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
    else:
        # Interactive mode
        client.interactive_mode()


if __name__ == '__main__':
    main()
