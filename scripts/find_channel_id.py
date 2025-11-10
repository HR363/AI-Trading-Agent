"""
Find Telegram Channel ID - Discover channel IDs for channels you're a member of

This script helps you find the channel ID for any Telegram channel you're part of.
Simply run it and it will list all your channels with their IDs.
"""

import asyncio
import sys
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from loguru import logger

# Add parent directory to path to import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config

async def find_channels():
    """Find and list all Telegram channels/groups you're a member of"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              TELEGRAM CHANNEL ID FINDER                       ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Validate credentials
    if not all([Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH, Config.TELEGRAM_PHONE]):
        print("❌ Missing Telegram credentials in .env file!")
        print("\nRequired variables:")
        print("  - TELEGRAM_API_ID")
        print("  - TELEGRAM_API_HASH")
        print("  - TELEGRAM_PHONE")
        return
    
    try:
        # Create Telegram client
        client = TelegramClient(
            'channel_finder_session',
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
        
        print(f"🔗 Connecting to Telegram as {Config.TELEGRAM_PHONE}...")
        await client.start(phone=Config.TELEGRAM_PHONE)
        print("✅ Connected successfully!\n")
        
        print("📋 Searching for channels and groups...\n")
        print("=" * 70)
        
        # Get all dialogs (conversations)
        dialogs = await client.get_dialogs()
        
        channels_found = []
        groups_found = []
        
        for dialog in dialogs:
            entity = dialog.entity
            
            # Check if it's a channel or group
            if isinstance(entity, Channel):
                if entity.broadcast:
                    # It's a channel
                    channels_found.append({
                        'name': entity.title,
                        'id': entity.id,
                        'username': entity.username if entity.username else 'N/A'
                    })
                else:
                    # It's a supergroup
                    groups_found.append({
                        'name': entity.title,
                        'id': entity.id,
                        'username': entity.username if entity.username else 'N/A'
                    })
        
        # Display channels
        if channels_found:
            print(f"\n📢 CHANNELS ({len(channels_found)} found):")
            print("=" * 70)
            for i, channel in enumerate(channels_found, 1):
                print(f"\n{i}. {channel['name']}")
                print(f"   ID: {channel['id']}")
                print(f"   Username: @{channel['username']}" if channel['username'] != 'N/A' else "   Username: N/A")
                
                # Highlight if it matches our target
                if 'SNIPE TRADING PRO' in channel['name'].upper():
                    print("   ⭐ THIS LOOKS LIKE YOUR TARGET CHANNEL!")
        
        # Display groups
        if groups_found:
            print(f"\n\n👥 GROUPS ({len(groups_found)} found):")
            print("=" * 70)
            for i, group in enumerate(groups_found, 1):
                print(f"\n{i}. {group['name']}")
                print(f"   ID: {group['id']}")
                print(f"   Username: @{group['username']}" if group['username'] != 'N/A' else "   Username: N/A")
                
                # Highlight if it matches our target
                if 'SNIPE TRADING PRO' in group['name'].upper():
                    print("   ⭐ THIS LOOKS LIKE YOUR TARGET GROUP!")
        
        if not channels_found and not groups_found:
            print("\n⚠️  No channels or groups found!")
            print("   Make sure you're a member of the channel/group you're looking for.")
        
        print("\n" + "=" * 70)
        print("\n📝 NEXT STEPS:")
        print("1. Find 'SNIPE TRADING PRO' in the list above")
        print("2. Copy its ID (the number)")
        print("3. Add it to your .env file as: TELEGRAM_CHANNEL_ID=<the_id>")
        print("4. Make sure to include the negative sign if present (e.g., -1001234567890)")
        print("\n💡 TIP: Channel IDs usually start with -100")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Failed to find channels")
        print("\nTroubleshooting:")
        print("1. Make sure your Telegram credentials are correct")
        print("2. Check your internet connection")
        print("3. If you get a flood wait error, wait a few minutes and try again")

async def search_specific_channel(channel_name: str):
    """Search for a specific channel by name"""
    
    print(f"\n🔍 Searching specifically for: '{channel_name}'")
    
    if not all([Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH, Config.TELEGRAM_PHONE]):
        print("❌ Missing Telegram credentials!")
        return
    
    try:
        client = TelegramClient(
            'channel_finder_session',
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
        
        await client.start(phone=Config.TELEGRAM_PHONE)
        
        dialogs = await client.get_dialogs()
        
        found = False
        for dialog in dialogs:
            entity = dialog.entity
            if isinstance(entity, Channel):
                if channel_name.upper() in entity.title.upper():
                    found = True
                    print(f"\n✅ FOUND!")
                    print(f"   Name: {entity.title}")
                    print(f"   ID: {entity.id}")
                    print(f"   Username: @{entity.username}" if entity.username else "   Username: N/A")
                    print(f"   Type: {'Channel' if entity.broadcast else 'Group'}")
                    print(f"\n📋 Add this to your .env file:")
                    print(f"   TELEGRAM_CHANNEL_ID={entity.id}")
                    break
        
        if not found:
            print(f"\n❌ Could not find a channel named '{channel_name}'")
            print("   Make sure:")
            print("   - You're a member of this channel")
            print("   - The name is spelled correctly")
            print("   - Try running without a search term to see all channels")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Failed to search for channel")

def main():
    """Main entry point"""
    
    # Check if user provided a channel name to search for
    if len(sys.argv) > 1:
        channel_name = ' '.join(sys.argv[1:])
        asyncio.run(search_specific_channel(channel_name))
    else:
        asyncio.run(find_channels())

if __name__ == "__main__":
    main()
